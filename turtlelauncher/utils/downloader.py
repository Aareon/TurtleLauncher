import asyncio
import aiohttp
import zipfile
import tempfile
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class DownloadExtractUtility(QObject):
    progress_updated = Signal(int, str)  # percent, speed
    download_completed = Signal()
    extraction_completed = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.total_size = 0
        self.downloaded_size = 0
        self.start_time = 0

    async def download_and_extract(self, url, extract_path):
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_filename = Path(temp_file.name)

            # Download
            await self.download_file(url, temp_filename)
            self.download_completed.emit()

            # Extract
            await self.extract_zip(temp_filename, Path(extract_path))
            self.extraction_completed.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            # Clean up
            if temp_filename.exists():
                temp_filename.unlink()

    async def download_file(self, url, filename):
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

    async def extract_zip(self, zip_path, extract_path):
        total_size = sum(file.file_size for file in zipfile.ZipFile(zip_path).infolist())
        extracted_size = 0

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                zip_ref.extract(file, extract_path)
                extracted_size += file.file_size
                percent = int((extracted_size / total_size) * 100)
                self.progress_updated.emit(percent, "Extracting...")

    async def update_progress(self):
        percent = int((self.downloaded_size / self.total_size) * 100)
        elapsed_time = asyncio.get_event_loop().time() - self.start_time
        speed = self.downloaded_size / elapsed_time  # bytes per second
        speed_str = self.format_speed(speed)
        self.progress_updated.emit(percent, speed_str)

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

    @staticmethod
    def run_async(coro):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)