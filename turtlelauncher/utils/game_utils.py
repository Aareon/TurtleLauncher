from pathlib import Path
from loguru import logger
from turtlelauncher.utils.get_file_version import get_file_version
from turtlelauncher.utils.config import Config  # Only needed for type hinting
from turtlelauncher.utils.wow_version import ExeVersionExtractor


def check_game_installation(game_install_dir: Path | str, selected_binary: Path | str):
    logger.info("Checking game installation")
    if not game_install_dir:
        logger.debug("No game installation directory set in config")
        return False
    
    game_folder = Path(game_install_dir)
    logger.info(f"Checking for installation in: {game_folder}")
    
    game_binary = game_folder / "WoW.exe"
    data_folder = game_folder / "Data"

    if selected_binary:
        game_binary = Path(selected_binary)
        logger.debug(f"Using selected binary: {game_binary}")
    
    logger.debug(f"Checking for WoW.exe at: {game_binary}")
    logger.debug(f"Checking for Data folder at: {data_folder}")
    
    if game_binary.exists() and data_folder.is_dir():
        logger.info("Valid game installation found")
        return True
    else:
        if not game_binary.exists():
            logger.warning(f"{game_binary} not found")
        if not data_folder.is_dir():
            logger.warning("Data folder not found or not a directory")
        logger.info("Invalid or incomplete game installation")
        return False


def get_game_version(game_install_dir: Path | str):
    exe_path = Path(game_install_dir) / "WoW.exe"
    logger.debug(f"Attempting to get version for: {exe_path}")
    
    if exe_path.exists():
        try:
            version_info = ExeVersionExtractor.extract_version_info(str(exe_path))
            if version_info:
                version_str = f"Build {version_info.build_number} - v{version_info.version_number}"
                if version_info.is_beta:
                    version_str += " (Beta)"
                logger.debug(f"Extracted version: {version_str}")
                return version_str
            elif version_info is None:
                version = get_file_version(str(exe_path))
                if version:
                    logger.debug(f"WoW.exe version: {version}")
                    return version
                else:
                    logger.warning("Failed to retrieve WoW.exe version")
            else:
                logger.warning(f"WoW.exe not found at {exe_path}")
            return None
        except Exception as e:
            logger.exception(f"An error occurred while extracting version info: {str(e)}")
            return None


def update_game_install_dir(extracted_folder: Path | str, config: Config):
    install_dir = Path(config.game_install_dir)
    new_install_dir = install_dir / extracted_folder
    config.game_install_dir = str(new_install_dir)
    config.save()
    logger.info(f"Updated game_install_dir to: {config.game_install_dir}")
    return config
