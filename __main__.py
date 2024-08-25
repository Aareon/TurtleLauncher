import sys
from datetime import datetime
from PySide6.QtWidgets import QApplication
from turtlelauncher.windows.main_window import TurtleWoWLauncher
from turtlelauncher.utils.globals import TOOL_FOLDER
from loguru import logger
from turtlelauncher.__version__ import version


def setup_logging():
    # Determine if we're running as a compiled executable
    is_compiled = getattr(sys, 'frozen', False)

    # Create a timestamp for the log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"turtlewow_launcher_{timestamp}.log"

    # Set up logging configuration
    config = {
        "handlers": [
            {
                "sink": TOOL_FOLDER / "logs" / log_filename,
                "rotation": "10 MB",
                "retention": "1 week",
                "compression": "zip",
                "level": "INFO",
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            }
        ],
        "extra": {"user": "someone"}
    }

    # Add console logging if not compiled or if running in a terminal
    if not is_compiled or sys.stderr.isatty():
        config["handlers"].append({
            "sink": sys.stdout,
            "level": "INFO",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        })

    # Apply the configuration
    logger.configure(**config)

    if sys.stderr.isatty():
        logger.info("Running in console mode - logs will be displayed here")

if __name__ == "__main__":
    setup_logging()
    logger.info(f"Turtle WoW Launcher {version} starting...")
    
    app = QApplication(sys.argv)
    window = TurtleWoWLauncher()
    window.show()
    
    logger.info("Main window displayed")
    
    exit_code = app.exec()
    logger.info(f"Application closing with exit code: {exit_code}")
    sys.exit(exit_code)