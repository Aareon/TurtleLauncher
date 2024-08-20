from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStyleOption, QStyle, QLabel, QDialog, QMessageBox
from PySide6.QtGui import QFont, QPainter, QFontDatabase, QColor
from PySide6.QtCore import Slot, Signal, QTimer, Qt
from pathlib import Path
from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.image_button import ImageButton
from turtlelauncher.widgets.gradient_progressbar import GradientProgressBar
from turtlelauncher.utils.downloader import DownloadExtractUtility
from loguru import logger
import subprocess

from turtlelauncher.dialogs.stop_download import StopDownloadDialog
from turtlelauncher.dialogs.binary_select import BinarySelectionDialog

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"
DATA = HERE / "data"
IMAGES = ASSETS / "images"

class LauncherWidget(QWidget):
    download_completed = Signal()
    extraction_completed = Signal(str)
    error_occurred = Signal(str)
    download_button_clicked = Signal()
    play_button_clicked = Signal()
    settings_button_clicked = Signal()

    def __init__(self, check_game_installation_callback, config):
        super().__init__()

        self.check_game_installation_callback = check_game_installation_callback
        self.config = config
        logger.debug(f"LauncherWidget initialized with particles_disabled: {self.config.particles_disabled}")
        
        self.is_downloading = False
        self.initUI()

        # Update particle effect based on config
        self.update_particle_effect()

        self.download_utility = DownloadExtractUtility()
        self.download_utility.progress_updated.connect(self.update_progress)
        self.download_utility.download_completed.connect(self.on_download_completed)
        self.download_utility.extraction_completed.connect(self.on_extraction_completed)
        self.download_utility.error_occurred.connect(self.on_error)
        self.download_utility.status_changed.connect(self.on_status_changed)
        self.download_utility.total_size_updated.connect(self.set_total_file_size)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(str((FONTS / "alagard_by_pix3m.ttf").absolute()))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"  # Fallback font

        # Progress info layout
        progress_info_layout = QHBoxLayout()
        progress_info_layout.setContentsMargins(0, 0, 0, 5)

        self.progress_label = GradientLabel("Waiting...", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        self.progress_label.setFont(QFont(font_family, 14))
        self.progress_label.setMinimumWidth(300)  # Ensure enough width for the label
        progress_info_layout.addWidget(self.progress_label)

        progress_info_layout.addStretch()

        self.speed_label = QLabel("0 MB/s")
        self.speed_label.setFont(QFont(font_family, 10))
        self.speed_label.setStyleSheet("color: #ffd700;")
        progress_info_layout.addWidget(self.speed_label)

        self.total_size_label = QLabel("Total size: 0 MB")
        self.total_size_label.setFont(QFont(font_family, 10))
        self.total_size_label.setStyleSheet("color: #ffd700;")
        progress_info_layout.addWidget(self.total_size_label)

        main_layout.addLayout(progress_info_layout)

        self.progress_bar = GradientProgressBar()
        self.progress_bar.setAnimationSpeed(0.5)
        self.progress_bar.setGradientWidth(1000)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        main_layout.addWidget(self.progress_bar)

        self.update_particle_effect()

        # Version Label
        self.version_label = QLabel()
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.version_label.setStyleSheet("color: #ffd700; font-size: 14px;")
        self.version_label.hide()  # Initially hide the version label
        main_layout.addWidget(self.version_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.settings_button = ImageButton("PurpleButton.png", "Settings", "Alagard")
        
        # Modify the play_button to be a download/stop/play button
        self.action_button = ImageButton("PurpleButton.png", "Download", "Alagard")
        self.action_button.clicked.connect(self.on_action_button_clicked)


        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()
        button_layout.addWidget(self.action_button)

        main_layout.addLayout(button_layout)

        # Set semi-transparent background
        self.setStyleSheet("""
            LauncherWidget {
                background-color: rgba(26, 29, 36, 180);
            }
        """)

        # Set a maximum height for the LauncherWidget to limit vertical space usage
        self.setMaximumHeight(180)  # Adjust this value as needed

        # Connect the settings button click event to the new signal
        self.settings_button.clicked.connect(self.settings_button_clicked.emit)

        self.progress_bar.hide()
        self.progress_label.hide()
        self.speed_label.hide()
        self.total_size_label.hide()

    def paintEvent(self, event):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        painter.setOpacity(1)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
        super().paintEvent(event)

    def on_action_button_clicked(self):
        if self.action_button.text() == "Download":
            self.progress_label.setText("Waiting...")
            self.download_button_clicked.emit()
        elif self.action_button.text() == "Stop":
            self.stop_download()
        elif self.action_button.text() == "Play":
            if not self.config.selected_binary:
                self.open_binary_selection_dialog()
            else:
                self.execute_selected_binary()
    
    @Slot(str, str, str)
    def update_progress(self, percent, speed, state):
        percent_int = int(float(percent))
        if state == "extracting":
            if not self.progress_label.text().startswith("Extracting"):
                logger.info("Setting progress_label status to 'Extracting...'")
            self.progress_label.setText(f"Extracting... {percent_int}%")
            self.speed_label.hide()
            self.total_size_label.hide()
            self.progress_bar.show()  # Ensure progress bar is visible during extraction
        elif state == "downloading":
            self.progress_label.setText(f"Downloading... {percent_int}%")
            self.speed_label.show()
            self.speed_label.setText(speed)
            self.total_size_label.show()
            self.progress_bar.show()  # Ensure progress bar is visible during download
        self.progress_bar.setValue(percent_int)

    @Slot()
    def on_download_completed(self):
        self.progress_label.setText("Download completed. Preparing for extraction...")
        self.speed_label.hide()
        self.progress_bar.setValue(100)
        self.total_size_label.hide()
        self.progress_bar.show()  # Keep progress bar visible
        self.is_downloading = False
        logger.info("Download completed. Preparing for extraction...")
    
    @Slot()
    def on_verification_started(self):
        self.progress_label.setText("Verifying download...")
        self.speed_label.setText("")
        self.progress_bar.setValue(0)
    
    @Slot(bool)
    def on_verification_completed(self, is_valid):
        if is_valid:
            self.progress_label.setText("Verification successful. Preparing extraction...")
            self.progress_bar.setValue(100)
        else:
            self.progress_label.setText("Verification failed. Please try again.")
            self.progress_bar.setValue(0)
            self.progress_bar.stop_particle_effect()
            self.error_occurred.emit("Checksum verification failed")

    @Slot(str)
    def on_extraction_completed(self, extracted_folder):
        self.progress_label.setText("Installation completed!")
        self.speed_label.hide()
        self.progress_bar.setValue(100)
        self.progress_bar.stop_particle_effect()
        self.progress_bar.hide()  # Hide progress bar after extraction is complete
        self.action_button.setText("Play")  # Change the action button text to "Play"
        self.is_downloading = False
        self.extraction_completed.emit(extracted_folder)

    @Slot(str)
    def on_error(self, error_message):
        self.progress_label.setText(f"Error: {error_message}")
        self.speed_label.hide()  # Hide speed label on error
        self.progress_bar.stop_particle_effect()
        self.action_button.setText("Download")
        self.is_downloading = False
        self.error_occurred.emit(error_message)
    
    @Slot(bool)
    def on_status_changed(self, is_downloading):
        if is_downloading:
            if not self.config.particles_disabled:
                logger.debug("Download started, starting particle effect")
                self.progress_bar.start_particle_effect()
            else:
                logger.debug("Download started, but particles are disabled")
        else:
            logger.debug("Download stopped or completed, stopping particle effect")
            self.progress_bar.stop_particle_effect()
        
        # Show or hide speed label based on download status
        self.speed_label.setVisible(is_downloading)

    def set_play_mode(self):
        self.action_button.setText("Play")
        self.is_downloading = False

    def start_download(self, url, extract_path):
        self.progress_label.setText("Preparing download...")
        self.speed_label.setText("")
        self.speed_label.show()
        self.total_size_label.setText("Total size: Calculating...")
        self.progress_bar.setValue(0)
        self.action_button.setText("Stop")
        self.is_downloading = True
        logger.debug(f"Starting download from {url} to {extract_path}")
        
        # Only start particle effect if it's not disabled
        if not self.config.particles_disabled:
            logger.debug("Starting particle effect for download")
            self.progress_bar.start_particle_effect()
        else:
            logger.debug("Particles are disabled, not starting particle effect")

        QTimer.singleShot(0, lambda: self.download_utility.download_and_extract(url, extract_path))
    
    def stop_download(self):
        dialog = StopDownloadDialog(self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.download_utility.cancel_download()
            self.progress_label.setText("Download stopped")
            self.progress_bar.setValue(0)
            self.progress_bar.stop_particle_effect()
            self.action_button.setText("Download")
            self.is_downloading = False
            logger.info("Download stopped by user")
        else:
            logger.info("Download stop cancelled by user")

    def display_version_info(self, version):
        version_str = f"Turtle WoW Version: {version}"
        self.version_label.setText(version_str)
        self.version_label.show()
        self.total_size_label.hide()
        self.hide_progress_widgets()
        logger.info(f"Displaying version info: {version_str}")

    def hide_progress_widgets(self):
        self.progress_bar.hide()
        self.progress_label.hide()
        self.speed_label.hide()
        self.total_size_label.hide()

    def show_progress_widgets(self):
        self.progress_bar.show()
        self.progress_label.show()
        self.speed_label.show()
        self.total_size_label.show()
    
    @Slot(str)
    def set_total_file_size(self, total_size_str):
        try:
            total_size_bytes = int(total_size_str)
            if total_size_bytes > 0:
                if total_size_bytes >= 1024 * 1024 * 1024:  # If size is 1 GB or larger
                    total_size_gb = total_size_bytes / (1024 * 1024 * 1024)
                    self.total_size_label.setText(f"Total size: {total_size_gb:.2f} GB")
                else:
                    total_size_mb = total_size_bytes / (1024 * 1024)
                    self.total_size_label.setText(f"Total size: {total_size_mb:.2f} MB")
            else:
                self.total_size_label.setText("Total size: Unknown")
        except ValueError:
            logger.error(f"Invalid total size received: {total_size_str}")
            self.total_size_label.setText("Total size: Unknown")
        except Exception as e:
            logger.error(f"Error setting total file size: {e}")
            self.total_size_label.setText("Total size: Error")
        self.update_particle_effect()
    
    def update_particle_effect(self):
        logger.debug(f"Updating particle effect. Particles disabled: {self.config.particles_disabled}")
        if self.config.particles_disabled:
            logger.debug("Stopping particle effect")
            self.progress_bar.stop_particle_effect()
        elif self.is_downloading:
            logger.debug("Starting particle effect")
            self.progress_bar.start_particle_effect()
        else:
            logger.debug("Particle effect enabled, but not starting until download begins")
    
    def on_particles_setting_changed(self, particles_enabled):
        logger.debug(f"Particles setting changed: enabled = {particles_enabled}")
        self.config.particles_disabled = not particles_enabled
        self.update_particle_effect()
        if particles_enabled and self.is_downloading:
            logger.debug("Starting particle effect due to setting change during download")
            self.progress_bar.start_particle_effect()
        elif not particles_enabled:
            logger.debug("Stopping particle effect due to setting change")
            self.progress_bar.stop_particle_effect()
   
    def execute_selected_binary(self):
        if self.config.selected_binary:
            try:
                logger.info(f"Attempting to execute: {self.config.selected_binary}")
                subprocess.Popen(self.config.selected_binary, shell=True)
                logger.info("Binary execution initiated successfully")
            except Exception as e:
                error_message = f"Failed to execute the selected binary: {str(e)}"
                logger.error(error_message)
                QMessageBox.critical(self, "Execution Error", error_message)
        else:
            logger.warning("No binary selected for execution")
            QMessageBox.warning(self, "No Binary Selected", "Please select a binary to execute.")
    
    @Slot(str)
    def on_binary_selected(self, selected_binary):
        self.config.select_binary = selected_binary
        logger.info(f"Selected binary: {selected_binary}")
        self.play_button_clicked.emit()
    
    def open_binary_selection_dialog(self):
        dialog = BinarySelectionDialog(self.config, self)
        dialog.binary_selected.connect(self.on_binary_selected)
        dialog.exec()