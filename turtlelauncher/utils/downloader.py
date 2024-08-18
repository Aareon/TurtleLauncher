import asyncio
import aiohttp
import zipfile
import tempfile
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThreadPool, QRunnable
import logging

logger = logging.getLogger(__name__)

class DownloadExtractUtility(QObject):
    progress_updated = Signal(int, str)  # percent, speed
    download_completed = Signal()
    extraction_completed = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()

    def download_and_extract(self, url, extract_path):
        worker = DownloadExtractWorker(url, extract_path)
        worker.signals.progress_updated.connect(self.progress_updated)
        worker.signals.download_completed.connect(self.download_completed)
        worker.signals.extraction_completed.connect(self.extraction_completed)
        worker.signals.error_occurred.connect(self.error_occurred)
        self.thread_pool.start(worker)

class WorkerSignals(QObject):
    progress_updated = Signal(int, str)
    download_completed = Signal()
    extraction_completed = Signal()
    error_occurred = Signal(str)

class DownloadExtractWorker(QRunnable):
    def __init__(self, url, extract_path):
        super().__init__()
        self.url = url
        self.extract_path = Path(extract_path)
        self.signals = WorkerSignals()
        self.total_size = 0
        self.downloaded_size = 0
        self.start_time = 0

    def run(self):
        asyncio.run(self.async_run())

    async def async_run(self):
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_filename = Path(temp_file.name)

            # Download
            await self.download_file(self.url, temp_filename)
            self.signals.download_completed.emit()

            # Extract
            await self.extract_zip(temp_filename, self.extract_path)
            self.signals.extraction_completed.emit()

        except Exception as e:
            logger.exception("Error in download and extract process")
            self.signals.error_occurred.emit(str(e))
        finally:
            # Clean up
            if temp_filename.exists():
                temp_filename.unlink()

    async def download_file(self, url, filename):
        logger.debug(f"Starting download from {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                self.total_size = int(response.headers.get('content-length', 0))
                self.downloaded_size = 0
                self.start_time = asyncio.get_event_loop().time()

                with filename.open('wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        self.downloaded_size += len(chunk)
                        await self.update_progress()
        logger.debug("Download completed")

    async def extract_zip(self, zip_path, extract_path):
        logger.debug(f"Starting extraction to {extract_path}")
        total_size = sum(file.file_size for file in zipfile.ZipFile(zip_path).infolist())
        extracted_size = 0

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                zip_ref.extract(file, extract_path)
                extracted_size += file.file_size
                percent = int((extracted_size / total_size) * 100)
                self.signals.progress_updated.emit(percent, "Extracting...")
        logger.debug("Extraction completed")

    async def update_progress(self):
        percent = int((self.downloaded_size / self.total_size) * 100)
        elapsed_time = asyncio.get_event_loop().time() - self.start_time
        speed = self.downloaded_size / elapsed_time if elapsed_time > 0 else 0  # bytes per second
        speed_str = self.format_speed(speed)
        self.signals.progress_updated.emit(percent, speed_str)

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