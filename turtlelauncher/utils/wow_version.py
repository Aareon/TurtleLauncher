import re
from typing import Optional, NamedTuple
from loguru import logger

class VersionInfo(NamedTuple):
    build_number: str
    version_number: str
    is_beta: bool

class ExeVersionExtractor:
    VERSION_PATTERN = re.compile(b'SET_GLUE_SCREEN\x00(\\d+)\x00\x00\x00\x00([\d.]+)\x00\x00RELEASE_BUILD')
    BETA_PATTERN = b'BETA_BUILD'

    @staticmethod
    def extract_version_info(file_path: str, show_beta: bool = False) -> Optional[VersionInfo]:
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
            
            match = ExeVersionExtractor.VERSION_PATTERN.search(content)
            
            if match:
                build_number = match.group(1).decode('ascii')
                version_number = match.group(2).decode('ascii')
                is_beta = ExeVersionExtractor.BETA_PATTERN in content[match.end():match.end()+20] if show_beta else ""
                
                return VersionInfo(build_number, version_number, is_beta)
            
            return None
        except Exception as e:
            logger.exception(f"An error occurred while extracting version info: {str(e)}")
            return None

    @staticmethod
    def get_version_string(file_path: str) -> str:
        version_info = ExeVersionExtractor.extract_version_info(file_path)
        if version_info:
            beta_str = " (Beta)" if version_info.is_beta else ""
            return f"Build {version_info.build_number} - v{version_info.version_number}{beta_str}"
        return "Version information not found"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        version_info = ExeVersionExtractor.extract_version_info(file_path)
        if version_info:
            print(f"Build Number: {version_info.build_number}")
            print(f"Version Number: {version_info.version_number}")
            print(f"Is Beta: {version_info.is_beta}")
        else:
            print("Failed to extract version information.")
    else:
        print("Please provide a file path as an argument.")