from pathlib import Path
import shutil
from loguru import logger


def clear_addon_settings(game_install_dir: Path):
    logger.debug("Clearing addon settings")
    wtf_path = Path(game_install_dir) / "WTF"
    
    if wtf_path.exists():
        if not any(wtf_path.iterdir()):
            logger.warning("WTF folder is empty")
            return "Warning", "The WTF folder is already empty."

        try:
            for item in wtf_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            logger.info("Successfully cleared addon settings")
            return "Success", "Addon settings have been cleared successfully."
        except Exception as e:
            logger.error(f"Error clearing addon settings: {str(e)}")
            return "Error", f"An error occurred while clearing addon settings: {str(e)}"
    else:
        logger.warning("WTF folder not found in the game installation directory")
        return "Warning", "WTF folder not found in the game installation directory."


def fix_black_screen(game_install_dir: Path):
    wtf_config_path = Path(game_install_dir) / "WTF" / "Config.wtf"
    
    if not wtf_config_path.exists():
        error_message = "Config.wtf file not found. Unable to apply Black Screen fix."
        logger.error(error_message)
        return "Error", error_message

    try:
        with open(wtf_config_path, 'r') as file:
            lines = file.readlines()

        gxWindow_found = False
        gxMaximize_found = False
        modified = False

        for i, line in enumerate(lines):
            if line.startswith('SET gxWindow '):
                gxWindow_found = True
                if not line.strip().endswith('"1"'):
                    lines[i] = 'SET gxWindow "1"\n'
                    modified = True
            elif line.startswith('SET gxMaximize '):
                gxMaximize_found = True
                if not line.strip().endswith('"1"'):
                    lines[i] = 'SET gxMaximize "1"\n'
                    modified = True

        if not gxWindow_found:
            lines.append('SET gxWindow "1"\n')
            modified = True
        if not gxMaximize_found:
            lines.append('SET gxMaximize "1"\n')
            modified = True

        if modified:
            with open(wtf_config_path, 'w') as file:
                file.writelines(lines)
            logger.info("Successfully applied Black Screen fix")
            return "Success", "Black Screen fix has been applied successfully."
        else:
            logger.info("Black Screen fix was already applied")
            return "Info", "Black Screen fix was already applied. No changes were needed."

    except Exception as e:
        error_message = f"An error occurred while applying Black Screen fix: {e}"
        logger.error(error_message)
        return "Error", error_message
    