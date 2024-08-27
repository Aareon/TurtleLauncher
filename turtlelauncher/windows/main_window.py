from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QMessageBox, QDialog, QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import QTimer, Qt, Slot, QEvent
from PySide6.QtGui import QPalette, QBrush, QImage, QFontDatabase, QIcon
from turtlelauncher.components.tweets_feed import TweetsFeed
from turtlelauncher.components.featured_content import FeaturedContent
from turtlelauncher.components.launcher import LauncherWidget
from turtlelauncher.widgets.image_overlay import ImageOverlay
from turtlelauncher.components.header import HeaderWidget
from turtlelauncher.utils.config import Config
from turtlelauncher.utils.globals import TOOL_FOLDER, IMAGES, FONTS, DATA, DOWNLOAD_URL
from turtlelauncher.dialogs.first_launch import FirstLaunchDialog
from turtlelauncher.dialogs.install_directory import InstallationDirectoryDialog
from turtlelauncher.utils.downloader import DownloadExtractUtility
from turtlelauncher.utils.game_utils import check_game_installation, get_game_version, update_game_install_dir
from pathlib import Path
from loguru import logger
from turtlelauncher.dialogs.install_status import InstallationStatusDialog
from turtlelauncher.dialogs.settings import SettingsDialog


class TurtleWoWLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Turtle WoW Launcher"))
        self.setMinimumSize(1200, 800)
        
        self.installEventFilter(self)
        
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
        logger.info(f"Using font family {font_family}")

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
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowActive:
                QTimer.singleShot(100, self.update_after_wake)
        return super().eventFilter(obj, event)

    def update_after_wake(self):
        logger.info("Updating components after wake from sleep")
        self.force_repaint()
        self.launcher_widget.update()
        self.tweets_widget.update()
        self.featured_content_widget.update()
        
        # Refresh dynamic content
        self.tweets_widget.refresh_tweets()
        self.featured_content_widget.refresh_content()
        
        # Update game version info
        self.update_launcher_with_game_version()
        
        # Reconnect any network-dependent components
        QApplication.processEvents()
    
    def check_first_launch(self):
        if not self.config.exists() or not self.config.valid() or not check_game_installation(self.config.game_install_dir, self.config.selected_binary):
            logger.info("No valid game installation found. Setting Download button.")
            self.launcher_widget.action_button.setText(self.tr("Download"))
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
            self.select_installation_directory(self.tr("Select Existing Installation Directory"))
        elif result == QDialog.DialogCode.Rejected:
            logger.debug("User chose to download the game")
            self.select_installation_directory(self.tr("Select Download Directory"))
        elif result == FirstLaunchDialog.CLOSED:
            logger.debug("First launch dialog was closed")
            self.cancel_setup()
        else:
            logger.debug("Unexpected result from first launch dialog")
            self.cancel_setup()

        # Ensure the dialog is deleted and the main window is updated
        dialog.deleteLater()
        QApplication.processEvents()
        self.update()
    
    def on_first_launch_dialog_finished(self, result):
        logger.debug(f"FirstLaunchDialog result: {result}")
        
        if result == QDialog.DialogCode.Accepted:
            logger.debug("User chose to select existing installation")
            self.select_installation_directory(self.tr("Select Existing Installation Directory"))
        elif result == QDialog.DialogCode.Rejected:
            logger.debug("User chose to download the game")
            self.select_installation_directory(self.tr("Select Download Directory"))
        else:
            logger.debug("First launch setup canceled")
            self.cancel_setup()
        
        # Ensure the dialog is deleted and the main window is updated
        self.first_launch_dialog.deleteLater()
        self.update()

    def cancel_setup(self):
        logger.debug("Cancelling setup")
        self.launcher_widget.hide_progress_widgets()
        self.launcher_widget.progress_label.setText(self.tr("Setup cancelled"))
        self.launcher_widget.action_button.setText(self.tr("Download"))
        QApplication.processEvents()
        self.update()

    def update_launcher_with_game_version(self):
        version = get_game_version(self.config.game_install_dir)
        if version:
            logger.info(f"Game version detected: {version}")
            self.launcher_widget.display_version_info(version)
        else:
            logger.warning("Game version could not be detected")
            self.launcher_widget.display_version_info(self.tr("Unknown"))
    
    def disable_main_window(self):
        self.setEnabled(False)
    
    def enable_main_window(self):
        self.setEnabled(True)

    def select_installation_directory(self, dialog_title):
        is_existing_install = dialog_title == self.tr("Select Existing Installation Directory")
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
                if check_game_installation(self.config.game_install_dir, self.config.selected_binary):
                    logger.debug("Valid existing installation selected")
                    self.launcher_widget.set_play_mode()
                    self.update_launcher_with_game_version()
                else:
                    logger.debug("Invalid installation directory selected")
                    QMessageBox.warning(
                        self,
                        self.tr("Invalid Installation"),
                        self.tr("The selected directory does not contain a valid Turtle WoW installation. Please choose a different directory or download a new copy of the game."))
                    self.setup_first_launch()
            else:
                self.launcher_widget.show_progress_widgets()
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
                if check_game_installation(self.config.game_install_dir, self.config.selected_binary):
                    logger.debug("Valid existing installation selected")
                    self.launcher_widget.set_play_mode()
                    self.update_launcher_with_game_version()
                else:
                    logger.debug("Invalid installation directory selected")
                    QMessageBox.warning(
                        self,
                        self.tr("Invalid Installation"),
                        self.tr("The selected directory does not contain a valid Turtle WoW installation.")
                    )
                    self.setup_first_launch()
            else:
                self.download_game()
        else:
            logger.debug("Installation directory selection canceled")
            self.cancel_setup()
        
        # Ensure the dialog is deleted and the main window is updated
        self.install_dir_dialog.deleteLater()
        self.update()

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
        tweets_widget = TweetsFeed(self.config, DATA / "tweets.json")
        tweets_widget.image_clicked.connect(self.show_image_overlay)
        featured_content_widget = FeaturedContent(self.config, content_type="turtletv", video_data=["https://turtle-wow.org/watch/embed/acfea246"])
        
        self.image_overlay = None
        
        tweets_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        featured_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        tweets_and_featured_layout.addWidget(tweets_widget, 1)
        tweets_and_featured_layout.addWidget(featured_content_widget, 2)
        content_layout.addLayout(tweets_and_featured_layout)

        main_layout.addWidget(content_widget, 1)

        # Launcher Widget
        self.launcher_widget = LauncherWidget(self, lambda: check_game_installation(self.config.game_install_dir, self.config.selected_binary), self.config)
        self.launcher_widget.download_completed.connect(self.on_download_completed)
        self.launcher_widget.extraction_completed.connect(self.on_extraction_completed)
        self.launcher_widget.download_button_clicked.connect(self.on_download_button_clicked)
        self.launcher_widget.error_occurred.connect(self.on_error)
        self.launcher_widget.settings_button_clicked.connect(self.open_settings)
        main_layout.addWidget(self.launcher_widget)

        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow {
                border: none;
            }
        """)

         # Update translations at the end of setup
        self.update_translations()

    def update_translations(self):
        self.setWindowTitle(self.tr("Turtle WoW Launcher"))
        
        # Update launcher widget texts
        self.launcher_widget.update_translations()
        
        # Update tray icon menu texts
        if hasattr(self, 'tray_icon'):
            show_action = self.tray_icon.contextMenu().actions()[0]
            quit_action = self.tray_icon.contextMenu().actions()[1]
            show_action.setText(self.tr("Show"))
            quit_action.setText(self.tr("Quit"))
    
    def open_settings(self):
        logger.debug("Opening settings dialog")
        settings_dialog = SettingsDialog(self, check_game_installation(self.config.game_install_dir, self.config.selected_binary), self.config)
        settings_dialog.particles_setting_changed.connect(self.launcher_widget.on_particles_setting_changed)
        settings_dialog.language_changed.connect(self.on_language_changed)
        settings_dialog.exec()
        logger.debug("Settings dialog closed")
    
    def on_language_changed(self, language):
        logger.info(f"Updating launcher language to: {language}")
        self.config.language = language
        self.config.save()
        self.update_translations()

    def on_download_button_clicked(self):
        logger.debug("Download button clicked")
        if not self.config.exists() or not self.config.valid() or not check_game_installation(self.config.game_install_dir, self.config.selected_binary):
            self.setup_first_launch()
        else:
            self.download_game()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction(self.tr("Show"))
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction(self.tr("Quit"))
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
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
            self.config = update_game_install_dir(extracted_folder, self.config)
            if check_game_installation(self.config.game_install_dir, self.config.selected_binary):
                version = get_game_version(self.config.game_install_dir)
                if version:
                    logger.info(f"Game version detected: {version}")
                    self.launcher_widget.display_version_info(version)
                    InstallationStatusDialog(self, "success", self.tr("Installation successful! Turtle WoW version {} is now ready to play.").format(version)).exec()
                else:
                    logger.warning("Game version could not be detected")
                    InstallationStatusDialog(self, "warning", self.tr("Installation complete, but the game version could not be detected.")).exec()
            else:
                logger.warning("Invalid or incomplete game installation after extraction")
                InstallationStatusDialog(self, "error", self.tr("The installation appears to be incomplete or invalid. Please try the installation process again.")).exec()
                self.setup_first_launch()  # Restart the setup process
        else:
            logger.error("Extraction completed but no folder name was provided")
            InstallationStatusDialog(self, "error", self.tr("Cannot identify the installation folder. Please try the installation process again.")).exec()
            self.setup_first_launch()  # Restart the setup process

    @Slot(str)
    def on_error(self, error_message):
        logger.error(f"Error occurred: {error_message}")
        InstallationStatusDialog(self, "error", self.tr("An error occurred: {}").format(error_message)).exec()

    def showEvent(self, event):
        super().showEvent(event)
        logger.debug("Main window shown")
    
    def closeEvent(self, event):
        if self.download_utility.is_downloading:
            reply = QMessageBox.question(
                self, self.tr('Exit Confirmation'),
                self.tr("A download is in progress. Do you want to:\n\n"
                "- Send the application to the system tray\n"
                "- Cancel the download and exit\n"
                "- Continue downloading"),
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
