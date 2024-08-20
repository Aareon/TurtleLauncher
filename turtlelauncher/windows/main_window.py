from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QMessageBox, QDialog, QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QPalette, QBrush, QImage, QFontDatabase, QIcon
from turtlelauncher.components.tweets_feed import TweetsFeed
from turtlelauncher.components.featured_content import FeaturedContent
from turtlelauncher.components.launcher import LauncherWidget
from turtlelauncher.widgets.image_overlay import ImageOverlay
from turtlelauncher.components.header import HeaderWidget
from turtlelauncher.utils.config import Config
from turtlelauncher.dialogs.first_launch import FirstLaunchDialog
from turtlelauncher.dialogs.install_directory import InstallationDirectoryDialog
from turtlelauncher.utils.downloader import DownloadExtractUtility
from turtlelauncher.utils.get_file_version import get_file_version
from pathlib import Path
from loguru import logger

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
DATA = ASSETS / "data"
IMAGES = ASSETS / "images"
FONTS = ASSETS / "fonts"

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
        
        # Set the window and taskbar icon
        icon_path = IMAGES / "turtle_wow_icon.png"
        icon = QIcon(str(icon_path))
        self.setWindowIcon(icon)

        # Set the taskbar icon (this is usually not necessary, but we're doing it explicitly)
        if QApplication.instance():
            QApplication.instance().setWindowIcon(icon)

        # Load the background image
        self.background_image = QImage(IMAGES / "background.png")

        # Set up the palette for the background
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(self.background_image))
        self.setPalette(palette)

        # Enable background auto-filling
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Load Fontinn font
        font_filename = "FontinSans_Cyrillic_R_46b.ttf"
        font_id = QFontDatabase.addApplicationFont(str((FONTS / font_filename).absolute()))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"
        logger.debug(f"Using font family {font_family}")

        # Load config
        self.config = Config(TOOL_FOLDER / "launcher.json")
        if not self.config.exists() or not self.config.load():
            logger.warning("Config does not exist or failed to load")
            self.config.game_install_dir = None

        # Initialize the DownloadExtractUtility
        self.download_utility = DownloadExtractUtility()
        self.download_utility.download_completed.connect(self.on_download_completed)
        self.download_utility.extraction_completed.connect(self.on_extraction_completed)
        self.download_utility.error_occurred.connect(self.on_error)
        
        self.setup_ui()
        self.setup_tray_icon()
        
        # Use QTimer to check for first launch after the main window is shown
        QTimer.singleShot(0, self.check_first_launch)
        
    def check_game_installation(self):
        logger.info("Checking game installation")
        if self.config.game_install_dir is None:
            logger.debug("No game installation directory set in config")
            return False
        
        game_folder = Path(self.config.game_install_dir)
        logger.info(f"Checking for installation in: {game_folder}")
        
        game_binary = game_folder / "WoW.exe"
        data_folder = game_folder / "Data"
        
        logger.debug(f"Checking for WoW.exe at: {game_binary}")
        logger.debug(f"Checking for Data folder at: {data_folder}")
        
        if game_binary.exists() and data_folder.is_dir():
            logger.info("Valid game installation found")
            return True
        else:
            if not game_binary.exists():
                logger.debug("WoW.exe not found")
            if not data_folder.is_dir():
                logger.debug("Data folder not found or not a directory")
            logger.info("Invalid or incomplete game installation")
            return False
    
    def check_first_launch(self):
        if not self.config.exists() or not self.config.valid() or not self.check_game_installation():
            logger.info("No valid game installation found. Setting Download button.")
            self.launcher_widget.action_button.setText("Download")
        else:
            logger.info("Valid game installation found.")
            self.launcher_widget.set_play_mode()
            self.update_launcher_with_game_version()

    def setup_first_launch(self):
        logger.debug("Setting up first launch")
        
        dialog = FirstLaunchDialog(self)
        dialog.setWindowModality(Qt.WindowModal)
        result = dialog.exec()

        logger.debug(f"FirstLaunchDialog result: {result}")
        
        if result == QDialog.DialogCode.Accepted:
            logger.debug("User chose to select existing installation")
            self.select_installation_directory("Select Existing Installation Directory")
        elif result == QDialog.DialogCode.Rejected:
            logger.debug("User chose to download the game")
            self.select_installation_directory("Select Download Directory")
        else:
            logger.debug("First launch setup canceled")
            self.cancel_setup()

        # Ensure the dialog is deleted and the main window is updated
        dialog.deleteLater()
        QApplication.processEvents()
        self.update()
    
    def on_first_launch_dialog_finished(self, result):
        logger.debug(f"FirstLaunchDialog result: {result}")
        
        if result == QDialog.DialogCode.Accepted:
            logger.debug("User chose to select existing installation")
            self.select_installation_directory("Select Existing Installation Directory")
        elif result == QDialog.DialogCode.Rejected:
            logger.debug("User chose to download the game")
            self.select_installation_directory("Select Download Directory")
        else:
            logger.debug("First launch setup canceled")
            self.cancel_setup()
        
        # Ensure the dialog is deleted and the main window is updated
        self.first_launch_dialog.deleteLater()
        self.update()

    def cancel_setup(self):
        self.launcher_widget.hide_progress_widgets()
        self.launcher_widget.progress_label.setText("Setup canceled")
        self.launcher_widget.action_button.setText("Download")
        QApplication.processEvents()
        self.update()

    def update_launcher_with_game_version(self):
        version = self.get_game_version()
        if version:
            logger.info(f"Game version detected: {version}")
            self.launcher_widget.display_version_info(version)
        else:
            logger.warning("Game version could not be detected")
            self.launcher_widget.display_version_info("Unknown")
    
    def disable_main_window(self):
        self.setEnabled(False)
    
    def enable_main_window(self):
        self.setEnabled(True)

    def select_installation_directory(self, dialog_title):
        is_existing_install = dialog_title == "Select Existing Installation Directory"
        install_dir_dialog = InstallationDirectoryDialog(self, is_existing_install)
        install_dir_dialog.setWindowTitle(dialog_title)
        install_dir_dialog.setWindowModality(Qt.WindowModal)
        result = install_dir_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            selected_directory = install_dir_dialog.selected_directory
            logger.debug(f"User selected {'existing' if is_existing_install else 'new'} installation directory: {selected_directory}")
            
            self.config.game_install_dir = Path(selected_directory)
            self.config.save()
            
            if is_existing_install:
                if self.check_game_installation():
                    logger.debug("Valid existing installation selected")
                    self.launcher_widget.set_play_mode()
                    self.update_launcher_with_game_version()
                else:
                    logger.debug("Invalid installation directory selected")
                    QMessageBox.warning(self, "Invalid Installation", "The selected directory does not contain a valid Turtle WoW installation.")
                    self.setup_first_launch()
            else:
                self.download_game()
        else:
            logger.debug("Installation directory selection canceled")
            self.cancel_setup()

        # Ensure the dialog is deleted and the main window is updated
        install_dir_dialog.deleteLater()
        QApplication.processEvents()
        self.update()
        self.force_repaint()
    
    def on_installation_directory_selected(self, result):
        if result == QDialog.DialogCode.Accepted:
            selected_directory = self.install_dir_dialog.selected_directory
            logger.debug(f"User selected {'existing' if self.install_dir_dialog.is_existing_install else 'new'} installation directory: {selected_directory}")
            
            self.config.game_install_dir = Path(selected_directory)
            self.config.save()
            
            if self.install_dir_dialog.is_existing_install:
                if self.check_game_installation():
                    logger.debug("Valid existing installation selected")
                    self.launcher_widget.set_play_mode()
                    self.update_launcher_with_game_version()
                else:
                    logger.debug("Invalid installation directory selected")
                    QMessageBox.warning(self, "Invalid Installation", "The selected directory does not contain a valid Turtle WoW installation.")
                    self.setup_first_launch()
            else:
                self.download_game()
        else:
            logger.debug("Installation directory selection canceled")
            self.cancel_setup()
        
        # Ensure the dialog is deleted and the main window is updated
        self.install_dir_dialog.deleteLater()
        self.update()
    
    def launch_game(self):
        # Implement game launching logic here
        logger.info("Launching the game")
        # For now, just show a message box
        QMessageBox.information(self, "Launch Game", "Game launching functionality not implemented yet.")

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
        featured_content_widget = FeaturedContent(content_type="video", video_id="FrIQy71OYtI")
        
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
        # Connect the download button signal to the first launch setup
        self.launcher_widget.download_button_clicked.connect(self.setup_first_launch)
        logger.debug("Connecting extraction_completed signal from `launcher_widget` to `on_extraction_completed` slot")
        self.launcher_widget.error_occurred.connect(self.on_error)
        main_layout.addWidget(self.launcher_widget)

        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow {
                border: none;
            }
        """)
    
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def update_game_install_dir(self, extracted_folder):
        install_dir = Path(self.config.game_install_dir)
        new_install_dir = install_dir / extracted_folder
        self.config.game_install_dir = str(new_install_dir)
        self.config.save()
        logger.info(f"Updated game_install_dir to: {self.config.game_install_dir}")
    
    def get_game_version(self):
        exe_path = Path(self.config.game_install_dir) / "WoW.exe"
        logger.debug(f"Attempting to get version for: {exe_path}")
        if exe_path.exists():
            version = get_file_version(str(exe_path))
            if version:
                logger.debug(f"WoW.exe version: {version}")
                return version
            else:
                logger.warning("Failed to retrieve WoW.exe version")
        else:
            logger.warning(f"WoW.exe not found at {exe_path}")
        return None
    
    def display_version_info(self, version):
        version_str = f"Turtle WoW Version: {version}"
        self.version_label.setText(version_str)
        self.version_label.show()
        self.launcher_widget.hide_progress_widgets()
        logger.info(f"Displaying version info: {version_str}")
    
    def show_progress_widgets(self):
        self.progress_bar.show()
        self.progress_label.show()
        self.speed_label.show()
        self.percent_label.show()
    
    def hide_progress_widgets(self):
        self.progress_bar.hide()
        self.progress_label.hide()
        self.speed_label.hide()
        self.percent_label.hide()

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
        
        # Resize and update the background image
        scaled_image = self.background_image.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(scaled_image))
        self.setPalette(palette)

        # Update the image overlay if it exists
        if self.image_overlay:
            self.image_overlay.setGeometry(self.rect())

        # Force a repaint of the entire window
        self.force_repaint()
    
    def download_game(self):
        install_dir = self.config.game_install_dir
        if install_dir:
            logger.debug(f"Game will be downloaded to: {install_dir}")
            self.launcher_widget.start_download(DOWNLOAD_URL, install_dir)
        else:
            logger.debug("No installation directory selected")
            self.close()

    def on_download_completed(self):
        logger.debug("Download completed")

    @Slot(str)
    def on_extraction_completed(self, extracted_folder):
        logger.info(f"Extraction completed. Extracted folder: {extracted_folder}")
        if extracted_folder:
            self.update_game_install_dir(extracted_folder)
            if self.check_game_installation():
                version = self.get_game_version()
                if version:
                    logger.info(f"Game version detected: {version}")
                    self.launcher_widget.display_version_info(version)
                else:
                    logger.warning("Game version could not be detected")
                QMessageBox.information(self, "Installation Complete", "Turtle WoW has been successfully installed!")
            else:
                logger.warning("Invalid or incomplete game installation after extraction")
                QMessageBox.warning(self, "Installation Issue", "The game files were extracted, but the installation seems incomplete. Please check the installation directory.")
                self.setup_first_launch()  # Restart the setup process
        else:
            logger.error("Extraction completed but no folder name was provided")
            QMessageBox.warning(self, "Installation Issue", "The game files were extracted, but there was an issue identifying the installation folder. Please check the installation directory.")
            self.setup_first_launch()  # Restart the setup process

    @Slot(str)
    def on_error(self, error_message):
        logger.error(f"Error occurred: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def showEvent(self, event):
        super().showEvent(event)
        logger.debug("Main window shown")
    
    def closeEvent(self, event):
        if self.download_utility.is_downloading:
            reply = QMessageBox.question(
                self, 'Exit Confirmation',
                "A download is in progress. Do you want to:\n\n"
                "- Send the application to the system tray\n"
                "- Cancel the download and exit\n"
                "- Continue downloading",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                event.ignore()
                self.hide()
                self.tray_icon.show()
            elif reply == QMessageBox.StandardButton.No:
                self.download_utility.cancel_download()
                self.quit_application()
            else:
                event.ignore()
        else:
            self.quit_application()
    
    def quit_application(self):
        self.download_utility.cancel_download()
        
        for child in self.children():
            if isinstance(child, QDialog) and child.isVisible():
                child.close()
        
        QTimer.singleShot(0, QApplication.quit)
    
    def force_repaint(self):
        self.repaint()
        for child in self.findChildren(QWidget):
            child.repaint()