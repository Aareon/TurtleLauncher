from pathlib import Path
from loguru import logger
import win32api
import win32con
import win32gui
import win32ui
from PIL import Image
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


def get_exe_icon(exe_path: Path):
    # Ensure the path is absolute and exists
    exe_path = exe_path.resolve()
    if not exe_path.exists() or exe_path.suffix.lower() != '.exe':
        raise ValueError("The provided path must be an existing .exe file")

    # Load the icon
    ico_x = win32gui.ExtractIcon(0, str(exe_path), 0)
    if ico_x == 0:
        raise RuntimeError(f"Could not extract icon from {exe_path}")

    # Get icon dimensions
    icon_info = win32gui.GetIconInfo(ico_x)
    icon_bmp = icon_info[3]  # hbmColor
    if icon_bmp == 0:  # If hbmColor is NULL, use hbmMask
        icon_bmp = icon_info[4]
    bmp_info = win32gui.GetObject(icon_bmp)
    icon_width, icon_height = bmp_info.bmWidth, bmp_info.bmHeight

    # Create a device context and bitmap
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, icon_width, icon_height)
    hdc = hdc.CreateCompatibleDC()

    # Draw the icon onto the bitmap
    hdc.SelectObject(hbmp)
    win32gui.DrawIconEx(hdc.GetHandleOutput(), 0, 0, ico_x, icon_width, icon_height, 0, None, win32con.DI_NORMAL)

    # Convert bitmap to bytes
    bmpstr = hbmp.GetBitmapBits(True)

    # Create PIL Image
    icon_image = Image.frombuffer(
        'RGBA',
        (icon_width, icon_height),
        bmpstr, 'raw', 'BGRA', 0, 1
    )

    # Clean up
    win32gui.DestroyIcon(ico_x)
    hdc.DeleteDC()
    win32gui.ReleaseDC(0, hdc.GetHandleOutput())
    win32gui.DeleteObject(hbmp.GetHandle())

    return icon_image


def get_file_version(file_path):
    try:
        # Get file information
        info = win32api.GetFileVersionInfo(file_path, "\\")
        
        # Get the file version
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        
        # Extract version numbers
        version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
        
        return version
    except Exception as e:
        return f"Error: {str(e)}"



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
