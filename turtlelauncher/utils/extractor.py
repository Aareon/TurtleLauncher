import asyncio
import zipfile
import concurrent.futures
from pathlib import Path
from loguru import logger

class ExtractionWorker:
    def __init__(self, max_workers=16):
        self.MAX_WORKERS = max_workers

    async def extract_zip(self, zip_path, extract_path, progress_callback=None):
        logger.info(f"Starting extraction: {zip_path} to {extract_path}")
        loop = asyncio.get_running_loop()
        zip_path = Path(zip_path)
        extract_path = Path(extract_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total_size = sum(file.file_size for file in zip_ref.infolist())
            extracted_size = 0
            extracted_folder = None

            def extract_file(file):
                nonlocal extracted_size, extracted_folder
                if not extracted_folder and not file.filename.startswith('__MACOSX'):
                    extracted_folder = file.filename.split('/')[0]
                zip_ref.extract(file, extract_path)
                extracted_size += file.file_size
                if progress_callback:
                    percent = int((extracted_size / total_size) * 100)
                    loop.call_soon_threadsafe(progress_callback, percent, "Extracting...")

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as pool:
                await loop.run_in_executor(pool, lambda: list(map(extract_file, zip_ref.infolist())))

        logger.info("Extraction completed successfully")
        return extracted_folder

    @staticmethod
    async def is_zip_file(file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                return True
        except zipfile.BadZipFile:
            return False
        except Exception as e:
            logger.error(f"Error checking if file is a zip: {e}")
            return False