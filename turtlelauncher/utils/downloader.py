import httpx
import asyncio
import zipfile
import tempfile
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from loguru import logger
import time

# Configure logger
logger.remove()
logger.add("downloader.log", rotation="10 MB", level="INFO")
logger.add(lambda msg: print(msg, end=""), level="INFO")  # Also print to console

class WorkerSignals(QObject):
    progress_updated = Signal(int, str)
    download_completed = Signal()
    extraction_completed = Signal(str)
    error_occurred = Signal(str)
    total_size_updated = Signal(str)

class DownloadExtractWorker(QRunnable):
    CHUNK_SIZE = 1024 * 1024  # 1 MB
    SPEED_UPDATE_INTERVAL = 0.5  # seconds
    LOG_INTERVAL = 10  # seconds

    def __init__(self, url, extract_path):
        super().__init__()
        self.url = url
        self.extract_path = Path(extract_path)
        self.signals = WorkerSignals()
        self.is_cancelled = False
        logger.info(f"DownloadExtractWorker initialized for URL: {url}")

    def run(self):
        logger.info("Starting DownloadExtractWorker run")
        asyncio.run(self.async_run())

    async def async_run(self):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_filename = Path(temp_file.name)
            logger.info(f"Created temporary file: {temp_filename}")

            await self.download_file(self.url, temp_filename)
            self.signals.download_completed.emit()
            logger.info("Download completed")

            extracted_folder = await self.extract_zip(temp_filename, self.extract_path)
            self.signals.extraction_completed.emit(extracted_folder)
            logger.info(f"Extraction completed. Extracted folder: {extracted_folder}")

        except asyncio.CancelledError:
            logger.warning("Download cancelled")
            self.signals.error_occurred.emit("Download cancelled")
        except Exception as e:
            logger.exception(f"Error in download and extract process: {e}")
            self.signals.error_occurred.emit(str(e))
        finally:
            if temp_filename.exists():
                temp_filename.unlink()
                logger.info(f"Temporary file removed: {temp_filename}")

    async def download_file(self, url, filename):
        logger.info(f"Starting download: {url} to {filename}")
        total_size = 0
        downloaded_size = 0
        start_time = time.time()
        last_update_time = start_time
        last_log_time = start_time

        async with httpx.AsyncClient(http2=True, timeout=None) as client:
            try:
                async with client.stream('GET', url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get('Content-Length', 0))
                    logger.info(f"Total file size: {self.format_size(total_size)}")
                    logger.info(f"Using HTTP version: {response.http_version}")
                    self.signals.total_size_updated.emit(str(total_size))

                    with filename.open('wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=self.CHUNK_SIZE):
                            if self.is_cancelled:
                                logger.warning("Download cancelled")
                                raise asyncio.CancelledError()

                            f.write(chunk)
                            downloaded_size += len(chunk)

                            current_time = time.time()
                            if current_time - last_update_time >= self.SPEED_UPDATE_INTERVAL:
                                self.update_progress(downloaded_size, total_size, current_time - start_time)
                                last_update_time = current_time

                            if current_time - last_log_time >= self.LOG_INTERVAL:
                                progress = downloaded_size / total_size if total_size > 0 else 0
                                logger.info(f"Download progress: {progress:.2%}")
                                last_log_time = current_time

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"An error occurred while requesting {e.request.url!r}.")
                raise

        logger.info("Download completed successfully")

    def update_progress(self, downloaded_size, total_size, elapsed_time):
        speed = downloaded_size / elapsed_time
        percent = int((downloaded_size / total_size) * 100) if total_size > 0 else 0
        speed_str = self.format_speed(speed)
        logger.debug(f"Progress: {percent}%, Speed: {speed_str}")
        self.signals.progress_updated.emit(percent, speed_str)

    async def extract_zip(self, zip_path, extract_path):
        logger.info(f"Starting extraction: {zip_path} to {extract_path}")
        total_size = sum(file.file_size for file in zipfile.ZipFile(zip_path).infolist())
        extracted_size = 0
        extracted_folder = None

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                if self.is_cancelled:
                    logger.warning("Extraction cancelled")
                    raise asyncio.CancelledError()

                if not extracted_folder and not file.filename.startswith('__MACOSX'):
                    extracted_folder = file.filename.split('/')[0]

                zip_ref.extract(file, extract_path)
                extracted_size += file.file_size
                percent = int((extracted_size / total_size) * 100)
                self.signals.progress_updated.emit(percent, "Extracting...")

                if extracted_size % (10 * self.CHUNK_SIZE) == 0:
                    logger.info(f"Extraction progress: {percent}%")

        logger.info(f"Extraction completed. Extracted folder: {extracted_folder}")
        return extracted_folder

    @staticmethod
    def format_speed(speed):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if speed < 1024:
                return f"{speed:.2f} {unit}/s"
            speed /= 1024
        return f"{speed:.2f} TB/s"

    @staticmethod
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    def cancel(self):
        logger.info("Cancellation requested")
        self.is_cancelled = True

class DownloadExtractUtility(QObject):
    progress_updated = Signal(str, str)
    download_completed = Signal()
    extraction_completed = Signal(str)
    error_occurred = Signal(str)
    status_changed = Signal(bool)
    total_size_updated = Signal(str)

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
        self.current_worker.signals.total_size_updated.connect(self.on_total_size_updated)

        self.is_downloading = True
        self.thread_pool.start(self.current_worker)

    def cancel_download(self):
        logger.info("Cancelling download")
        if self.current_worker:
            self.current_worker.cancel()
        self.thread_pool.clear()
        self.is_downloading = False

    def on_progress_updated(self, percent, speed):
        logger.debug(f"Progress update: {percent}%, Speed: {speed}")
        self.progress_updated.emit(str(percent), speed)

    def on_download_completed(self):
        logger.info("Download phase completed")
        self.download_completed.emit()

    def on_extraction_completed(self, extracted_folder):
        logger.info(f"Extraction completed. Extracted folder: {extracted_folder}")
        self.is_downloading = False
        self.extraction_completed.emit(extracted_folder)

    def on_error(self, error_message):
        logger.error(f"Error in download/extract process: {error_message}")
        self.is_downloading = False
        self.error_occurred.emit(error_message)

    def on_total_size_updated(self, total_size):
        logger.info(f"Total file size: {DownloadExtractWorker.format_size(int(total_size))}")
        self.total_size_updated.emit(total_size)