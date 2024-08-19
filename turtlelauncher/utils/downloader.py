import asyncio
import aiohttp
import zipfile
import tempfile
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, QMetaObject, Qt, Slot
import logging
import time

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    progress_updated = Signal(int, str)
    download_completed = Signal()
    extraction_completed = Signal()
    error_occurred = Signal(str)

class DownloadExtractWorker(QRunnable):
    STALL_TIMEOUT = 30  # seconds
    MAX_RETRIES = 5
    RETRY_DELAY = 5  # seconds
    SPEED_UPDATE_INTERVAL = 0.5  # seconds

    def __init__(self, url, extract_path):
        super().__init__()
        self.url = url
        self.extract_path = Path(extract_path)
        self.signals = WorkerSignals()
        self.is_cancelled = False
        self.loop = None
        self.last_progress_time = 0
        self.last_downloaded_size = 0
        self.retry_count = 0
        self.last_speed_update_time = 0
        self.last_speed_string = "0 B/s"
        logger.info(f"Initialized DownloadExtractWorker for URL: {url}")

    def run(self):
        logger.info("Starting DownloadExtractWorker run")
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.async_run())
        except Exception as e:
            logger.exception("Unexpected error in DownloadExtractWorker run")
        finally:
            if self.loop:
                self.loop.close()
            logger.info("DownloadExtractWorker run completed")

    async def async_run(self):
        logger.info("Starting async_run")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_filename = Path(temp_file.name)
            logger.info(f"Created temporary file: {temp_filename}")

            await self.download_file(self.url, temp_filename)
            self.signals.download_completed.emit()
            logger.info("Download completed")

            logger.info(f"Starting extraction to {self.extract_path}")
            await self.extract_zip(temp_filename, self.extract_path)
            self.signals.extraction_completed.emit()
            logger.info("Extraction completed")

        except asyncio.CancelledError:
            logger.warning("Download cancelled")
            self.signals.error_occurred.emit("Download cancelled")
        except Exception as e:
            logger.exception("Error in download and extract process")
            self.signals.error_occurred.emit(str(e))
        finally:
            if temp_filename.exists():
                temp_filename.unlink()
                logger.info(f"Temporary file removed: {temp_filename}")
    
    async def check_resume_support(self, url):
        logger.info(f"Checking resume support for URL: {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    accepts_ranges = response.headers.get('Accept-Ranges', '').lower()
                    supports_resume = accepts_ranges == 'bytes'
                    logger.info(f"Resume support: {'Yes' if supports_resume else 'No'}")
                    return supports_resume
        except aiohttp.ClientError as e:
            logger.error(f"Error checking resume support: {e}")
            return False

    async def download_file(self, url, filename):
        logger.info(f"Starting download: {url} to {filename}")
        total_size = 0
        downloaded_size = 0
        supports_resume = await self.check_resume_support(url)
        
        while self.retry_count < self.MAX_RETRIES:
            try:
                headers = {}
                if supports_resume and filename.exists():
                    downloaded_size = filename.stat().st_size
                    headers['Range'] = f'bytes={downloaded_size}-'
                    logger.info(f"Resuming download from byte {downloaded_size}")
                    self.retry_count = 0  # Reset retry count when resuming
                else:
                    downloaded_size = 0
                    logger.info("Starting download from the beginning")

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 416:
                            logger.info("File already fully downloaded")
                            return

                        if total_size == 0:
                            content_range = response.headers.get('Content-Range')
                            if content_range:
                                total_size = int(content_range.split('/')[-1])
                            else:
                                total_size = int(response.headers.get('Content-Length', 0))
                            logger.info(f"Total file size: {total_size} bytes")

                        mode = 'ab' if supports_resume and downloaded_size > 0 else 'wb'
                        with filename.open(mode) as f:
                            async for chunk in response.content.iter_chunked(8192):
                                if self.is_cancelled:
                                    logger.warning("Download cancelled")
                                    raise asyncio.CancelledError()
                                
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                
                                current_time = time.time()
                                if current_time - self.last_speed_update_time >= self.SPEED_UPDATE_INTERVAL:
                                    percent = int((downloaded_size / total_size) * 100) if total_size > 0 else 0
                                    speed = self.calculate_speed(downloaded_size, current_time)
                                    logger.debug(f"Download progress: {percent}%, Speed: {speed}")
                                    self.signals.progress_updated.emit(percent, speed)
                                    self.last_speed_update_time = current_time

                                if self.is_stalled(downloaded_size):
                                    logger.warning("Download stalled. Retrying...")
                                    raise asyncio.TimeoutError()
                                
                                self.last_downloaded_size = downloaded_size
                                self.last_progress_time = current_time

                        if downloaded_size >= total_size:
                            logger.info("Download completed successfully")
                            return

            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                self.retry_count += 1
                logger.warning(f"Download error (attempt {self.retry_count}/{self.MAX_RETRIES}): {e}")
                if self.retry_count >= self.MAX_RETRIES:
                    logger.error(f"Max retries reached. Download failed: {e}")
                    raise Exception(f"Max retries reached. Download failed: {e}")
                logger.info(f"Retrying download in {self.RETRY_DELAY} seconds...")
                await asyncio.sleep(self.RETRY_DELAY)

        raise Exception("Max retries reached. Download failed.")
    
    def is_stalled(self, current_size):
        if time.time() - self.last_progress_time > self.STALL_TIMEOUT:
            return current_size == self.last_downloaded_size
        return False

    def calculate_speed(self, current_size, current_time):
        elapsed_time = current_time - self.last_speed_update_time
        if elapsed_time > 0:
            speed = (current_size - self.last_downloaded_size) / elapsed_time
            return self.format_speed(speed)
        return "0 B/s"

    async def extract_zip(self, zip_path, extract_path):
        logger.info(f"Starting extraction: {zip_path} to {extract_path}")
        total_size = sum(file.file_size for file in zipfile.ZipFile(zip_path).infolist())
        extracted_size = 0

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                if self.is_cancelled:
                    logger.warning("Extraction cancelled")
                    raise asyncio.CancelledError()
                zip_ref.extract(file, extract_path)
                extracted_size += file.file_size
                percent = int((extracted_size / total_size) * 100)
                logger.debug(f"Extraction progress: {percent}%")
                self.signals.progress_updated.emit(percent, "Extracting...")

        logger.info("Extraction completed successfully")

    @staticmethod
    def format_speed(speed):
        if speed < 1024:
            return f"{speed:.2f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed/1024:.2f} KB/s"
        elif speed < 1024 * 1024 * 1024:
            return f"{speed/(1024*1024):.2f} MB/s"
        else:
            return f"{speed/(1024*1024*1024):.2f} GB/s"

    def cancel(self):
        logger.info("Cancellation requested")
        self.is_cancelled = True
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

class DownloadExtractUtility(QObject):
    progress_updated = Signal(int, str)  # percent, speed
    download_completed = Signal()
    extraction_completed = Signal()
    error_occurred = Signal(str)
    status_changed = Signal(bool)  # True if downloading, False otherwise

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.current_worker = None
        self._is_downloading = False
        logger.info("DownloadExtractUtility initialized")

    @property
    def is_downloading(self):
        return self._is_downloading

    @is_downloading.setter
    def is_downloading(self, value):
        if self._is_downloading != value:
            self._is_downloading = value
            logger.info(f"Download status changed: {'Active' if value else 'Inactive'}")
            self.status_changed.emit(value)

    def download_and_extract(self, url, extract_path):
        logger.info(f"Starting download and extract process: URL={url}, Path={extract_path}")
        self.current_worker = DownloadExtractWorker(url, extract_path)
        self.current_worker.signals.progress_updated.connect(self.on_progress_updated)
        self.current_worker.signals.download_completed.connect(self.on_download_completed)
        self.current_worker.signals.extraction_completed.connect(self.on_extraction_completed)
        self.current_worker.signals.error_occurred.connect(self.on_error)
        
        self.is_downloading = True
        self.thread_pool.start(self.current_worker)

    def cancel_download(self):
        logger.info("Cancelling download")
        if self.current_worker:
            self.current_worker.cancel()
        self.thread_pool.clear()
        self.is_downloading = False

    @Slot(int, str)
    def on_progress_updated(self, percent, speed):
        logger.debug(f"Progress update: {percent}%, Speed: {speed}")
        self.progress_updated.emit(percent, speed)

    @Slot()
    def on_download_completed(self):
        logger.info("Download completed")
        self.download_completed.emit()

    @Slot()
    def on_extraction_completed(self):
        logger.info("Extraction completed")
        self.is_downloading = False
        self.extraction_completed.emit()

    @Slot(str)
    def on_error(self, error_message):
        logger.error(f"Error in download/extract process: {error_message}")
        self.is_downloading = False
        self.error_occurred.emit(error_message)


# Logging configuration
def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    # Set more verbose logging for our module
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    
    # Set less verbose logging for third-party libraries
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

configure_logging()