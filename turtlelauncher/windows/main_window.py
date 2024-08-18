from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QMessageBox, QFileDialog, QPushButton, QDialog, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPalette, QBrush
from turtlelauncher.components.tweets_feed import TweetsFeed
from turtlelauncher.components.featured_content import FeaturedContent
from turtlelauncher.components.launcher import LauncherWidget
from turtlelauncher.widgets.image_overlay import ImageOverlay
from turtlelauncher.components.header import HeaderWidget
from turtlelauncher.utils.config import Config
from turtlelauncher.dialogs.first_launch import FirstLaunchDialog
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
DATA = ASSETS / "data"
IMAGES = ASSETS / "images"

USER_DOCUMENTS = Path.home() / "Documents"
TOOL_FOLDER = USER_DOCUMENTS / "TurtleLauncher"
if not TOOL_FOLDER.exists():
    TOOL_FOLDER.mkdir(parents=True)

DOWNLOAD_URL = "https://turtle-eu.b-cdn.net/twmoa_1171.zip"


class TurtleWoWLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Turtle WoW Launcher")
        self.setMinimumSize(1200, 800)
        
        # Set the window icon
        icon = QPixmap(IMAGES / "turtle_wow_icon.png")
        self.setWindowIcon(icon)

        # Set background image
        background = QPixmap(IMAGES / "background.png")
        background_brush = QBrush(background)
        palette = self.palette()
        palette.setBrush(QPalette.Window, background_brush)
        self.setPalette(palette)

        # Load config
        self.config = Config(TOOL_FOLDER / "launcher.json")
        
        self.setup_ui()
        
        # Use QTimer to check for first launch after the main window is shown
        QTimer.singleShot(0, self.check_first_launch)
    
    def check_first_launch(self):
        if not self.config.exists() or not self.config.valid():
            self.setup_first_launch()
        else:
            self.config.load()

    def setup_first_launch(self):
        logger.debug("Setting up first launch")
        dialog = FirstLaunchDialog(self)
        logger.debug("FirstLaunchDialog created")
        
        # Force the dialog to be on top
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # Show the dialog and wait for it to be visible
        dialog.show()
        QApplication.processEvents()
        
        logger.debug(f"Dialog visible: {dialog.isVisible()}")
        logger.debug(f"Dialog geometry: {dialog.geometry()}")
        
        result = dialog.exec()
        logger.debug(f"Dialog result: {result}")
        
        if result == QDialog.DialogCode.Accepted:
            logger.debug("User chose to select existing installation")
            self.select_existing_installation()
        elif result == QDialog.DialogCode.Rejected:
            logger.debug("User chose to download the game")
            self.download_game()
        else:
            logger.debug("First launch setup canceled")
            self.close()

    def select_existing_installation(self):
        install_dir = QFileDialog.getExistingDirectory(self, "Select Turtle WoW Installation Directory")
        if install_dir:
            self.config.game_install_dir = str(Path(install_dir))
            self.config.save()
            logger.debug(f"Existing installation selected: {self.config.game_install_dir}")
        else:
            logger.debug("No installation directory selected")
            self.close()  # Close the launcher if no directory is selected

    def download_game(self):
        self.config.game_install_dir = str(TOOL_FOLDER / "TurtleWoW")
        self.config.save()
        logger.debug(f"Game will be downloaded to: {self.config.game_install_dir}")
        QTimer.singleShot(0, lambda: self.launcher_widget.start_download(DOWNLOAD_URL, self.config.game_install_dir))

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setAutoFillBackground(False)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_widget = HeaderWidget()
        main_layout.addWidget(header_widget)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        tweets_and_featured_layout = QHBoxLayout()
        tweets_widget = TweetsFeed(DATA / "tweets.json")
        tweets_widget.image_clicked.connect(self.show_image_overlay)
        featured_content_widget = FeaturedContent()
        
        self.image_overlay = None
        
        tweets_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        featured_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        tweets_and_featured_layout.addWidget(tweets_widget, 1)
        tweets_and_featured_layout.addWidget(featured_content_widget, 2)
        content_layout.addLayout(tweets_and_featured_layout)

        main_layout.addWidget(content_widget, 1)

        # Launcher Widget
        self.launcher_widget = LauncherWidget()
        self.launcher_widget.download_completed.connect(self.on_download_completed)
        self.launcher_widget.extraction_completed.connect(self.on_extraction_completed)
        self.launcher_widget.error_occurred.connect(self.on_error)
        main_layout.addWidget(self.launcher_widget)

        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow {
                border: none;
            }
        """)

    def show_image_overlay(self, pixmap):
        if self.image_overlay:
            self.image_overlay.close()
        
        self.image_overlay = ImageOverlay(pixmap, self)
        self.image_overlay.closed.connect(self.on_overlay_closed)
        
        self.image_overlay.setGeometry(self.rect())
        self.image_overlay.show()
    
    def on_overlay_closed(self):
        self.image_overlay = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_overlay:
            self.image_overlay.setGeometry(self.rect())
    
    def on_download_completed(self):
        logger.debug("Download completed")

    def on_extraction_completed(self):
        logger.debug("Extraction completed")
        QMessageBox.information(self, "Installation Complete", "Turtle WoW has been successfully installed!")

    def on_error(self, error_message):
        logger.error(f"Error occurred: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def showEvent(self, event):
        super().showEvent(event)
        logger.debug("Main window shown")