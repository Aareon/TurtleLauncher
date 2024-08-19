import sys
import os
from PySide6.QtWidgets import QApplication
from turtlelauncher.windows.main_window import TurtleWoWLauncher
from loguru import logger

def setup_logging():
    # Determine if we're running as a compiled executable
    is_compiled = getattr(sys, 'frozen', False)

    # Set up logging configuration
    config = {
        "handlers": [
            {
                "sink": "logs/turtlewow_launcher.log",
                "rotation": "10 MB",
                "retention": "1 week",
                "compression": "zip",
                "level": "INFO",
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            }
        ],
        "extra": {"user": "someone"}
    }

    # Add console logging only if not compiled
    if not is_compiled:
        config["handlers"].append({
            "sink": sys.stdout,
            "level": "INFO",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        })

    # Apply the configuration
    logger.configure(**config)

if __name__ == "__main__":
    setup_logging()
    logger.info("Application starting...")
    
    app = QApplication(sys.argv)
    window = TurtleWoWLauncher()
    window.show()
    
    logger.info("Main window displayed")
    
    exit_code = app.exec()
    logger.info(f"Application closing with exit code: {exit_code}")
    sys.exit(exit_code)