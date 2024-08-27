from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStyleOption, QStyle, QLabel, QDialog
from PySide6.QtGui import QFont, QPainter, QFontDatabase, QColor
from PySide6.QtCore import Slot, Signal, QTimer, Qt
from pathlib import Path
from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.image_button import ImageButton
from turtlelauncher.widgets.gradient_progressbar import GradientProgressBar
from turtlelauncher.utils.downloader import DownloadExtractUtility
from turtlelauncher.utils.globals import FONTS
from turtlelauncher.utils.game_utils import clear_cache
from loguru import logger
import subprocess
import sys
import os

from turtlelauncher.dialogs import show_error_dialog
from turtlelauncher.dialogs.stop_download import StopDownloadDialog
from turtlelauncher.dialogs.binary_select import BinarySelectionDialog
from turtlelauncher.dialogs.game_launch import GameLaunchDialog


class LauncherWidget(QWidget):
    download_completed = Signal()
    extraction_completed = Signal(str)
    error_occurred = Signal(str)
    download_button_clicked = Signal()
    play_button_clicked = Signal()
    settings_button_clicked = Signal()

    def __init__(self, parent, check_game_installation_callback, config):
        super().__init__()

        self.master = parent
        self.check_game_installation_callback = check_game_installation_callback
        self.config = config
        if not self.config._loaded:
            self.config.load()
            logger.info(f"Loaded config: {self.config}. Selected binary: {self.config.selected_binary}")
        else:
            logger.info(f"Config already loaded: {self.config}. Selected binary: {self.config.selected_binary}")
        logger.debug(f"LauncherWidget initialized with particles_disabled: {self.config.particles_disabled}")
        
        self.game_process = None
        self.game_launch_dialog = None
        self.process_monitor_timer = QTimer(self)
        self.process_monitor_timer.timeout.connect(self.check_game_process)
        
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

        self.progress_label = GradientLabel("", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        self.progress_label.setFont(QFont(font_family, 14))
        self.progress_label.setMinimumWidth(300)  # Ensure enough width for the label
        progress_info_layout.addWidget(self.progress_label)

        progress_info_layout.addStretch()

        self.speed_label = QLabel("")
        self.speed_label.setFont(QFont(font_family, 10))
        self.speed_label.setStyleSheet("color: #ffd700;")
        progress_info_layout.addWidget(self.speed_label)

        self.total_size_label = QLabel("")
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

        self.settings_button = ImageButton("PurpleButton.png", "", "Alagard")
        
        # Modify the play_button to be a download/stop/play button
        self.action_button = ImageButton("PurpleButton.png", "", "Alagard")
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

        # Update translations
        self.update_translations()
    
    def update_translations(self):
        self.progress_label.setText(self.tr("Waiting..."))
        self.speed_label.setText(self.tr("0 MB/s"))
        self.total_size_label.setText(self.tr("Total size: 0 MB"))
        self.settings_button.setText(self.tr("Settings"))
        self.update_action_button_state()

    def paintEvent(self, event):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        painter.setOpacity(1)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
        super().paintEvent(event)

    def on_action_button_clicked(self):
        current_text = self.action_button.text()
        if current_text == self.tr("Download"):
            self.progress_label.setText(self.tr("Waiting..."))
            self.download_button_clicked.emit()
        elif current_text == self.tr("Stop"):
            self.stop_download()
        elif current_text == self.tr("Play"):
            if not self.config.selected_binary:
                self.open_binary_selection_dialog()
            else:
                if self.validate_selected_binary():
                    self.execute_selected_binary()
                else:
                    self.open_binary_selection_dialog()
    
    @Slot(str, str, str)
    def update_progress(self, percent, speed, state):
        percent_int = int(float(percent))
        if state == "extracting":
            if not self.progress_label.text().startswith(self.tr("Extracting")):
                logger.info("Setting progress_label status to 'Extracting...'")
            self.progress_label.setText(self.tr("Extracting... {}%").format(percent_int))
            self.speed_label.hide()
            self.total_size_label.hide()
            self.progress_bar.show()  # Ensure progress bar is visible during extraction
        elif state == "downloading":
            self.progress_label.setText(self.tr("Downloading... {}%").format(percent_int))
            self.speed_label.show()
            self.speed_label.setText(speed)
            self.total_size_label.show()
            self.progress_bar.show()  # Ensure progress bar is visible during download
        self.progress_bar.setValue(percent_int)

    @Slot()
    def on_download_completed(self):
        self.progress_label.setText(self.tr("Download completed. Preparing for extraction..."))
        self.speed_label.hide()
        self.progress_bar.setValue(100)
        self.total_size_label.hide()
        self.progress_bar.show()  # Keep progress bar visible
        self.is_downloading = False
        logger.info("Download completed. Preparing for extraction...")
    
    @Slot()
    def on_verification_started(self):
        self.progress_label.setText(self.tr("Verifying download..."))
        self.speed_label.setText("")
        self.progress_bar.setValue(0)
    
    @Slot(bool)
    def on_verification_completed(self, is_valid):
        if is_valid:
            self.progress_label.setText(self.tr("Verification successful. Preparing extraction..."))
            self.progress_bar.setValue(100)
        else:
            self.progress_label.setText(self.tr("Verification failed. Please try again."))
            self.progress_bar.setValue(0)
            self.progress_bar.stop_particle_effect()
            self.error_occurred.emit(self.tr("Checksum verification failed"))

    @Slot(str)
    def on_extraction_completed(self, extracted_folder):
        self.progress_label.setText(self.tr("Installation completed!"))
        self.speed_label.hide()
        self.progress_bar.setValue(100)
        self.progress_bar.stop_particle_effect()
        self.progress_bar.hide()  # Hide progress bar after extraction is complete
        self.action_button.setText(self.tr("Play"))  # Change the action button text to "Play"
        self.is_downloading = False
        self.extraction_completed.emit(extracted_folder)

    @Slot(str)
    def on_error(self, error_message):
        self.progress_label.setText(self.tr("Error: {}").format(error_message))
        self.speed_label.hide()  # Hide speed label on error
        self.progress_bar.stop_particle_effect()
        self.action_button.setText(self.tr("Download"))
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
    
    def update_action_button_state(self):
        if self.check_game_installation_callback():
            self.action_button.setText(self.tr("Play"))
        else:
            self.action_button.setText(self.tr("Download"))

    def set_play_mode(self):
        self.action_button.setText(self.tr("Play"))
        self.is_downloading = False
        self.update_action_button_state()


    def start_download(self, url, extract_path):
        self.progress_label.setText(self.tr("Preparing download..."))
        self.speed_label.setText("")
        self.speed_label.show()
        self.total_size_label.setText(self.tr("Total size: Calculating..."))
        self.progress_bar.setValue(0)
        self.action_button.setText(self.tr("Stop"))
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
        dialog = StopDownloadDialog(self.master)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.download_utility.cancel_download()
            self.progress_label.setText(self.tr("Download stopped"))
            self.progress_bar.setValue(0)
            self.progress_bar.stop_particle_effect()
            self.action_button.setText(self.tr("Download"))
            self.is_downloading = False
            logger.info("Download stopped by user")
        else:
            logger.info("Download stop cancelled by user")

    def display_version_info(self, version):
        version_str = self.tr("Turtle WoW Version: {}").format(version)
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
   
    def check_game_process(self):
        if self.game_process:
            return_code = self.game_process.poll()
            if return_code is not None:
                # Process has ended
                self.process_monitor_timer.stop()
                if self.game_launch_dialog:
                    self.game_launch_dialog.close()
                
                stdout, stderr = self.game_process.communicate()
                if return_code != 0 or stderr:
                    error_message = self.tr("Game process ended unexpectedly. Return code: {}\n").format(return_code)
                    if stderr:
                        error_message += self.tr("Error output: {}").format(stderr.decode('utf-8', errors='replace'))
                    logger.error(error_message)
                    if self.game_launch_dialog:
                        self.game_launch_dialog.close()
                    show_error_dialog(self.master, self.tr("Game Execution Error"), error_message)
                else:
                    logger.info("Game process has ended normally")

                self.game_process = None
   
    @Slot()
    def on_launch_completed(self):
        logger.info("Game launch completed")
    
    def validate_selected_binary(self):
        if self.config.selected_binary:
            binary_path = Path(self.config.selected_binary)
            try:
                if not binary_path.exists():
                    logger.warning(f"Selected binary no longer exists: {binary_path}")
                    self.config.selected_binary = None
                    if self.game_launch_dialog:
                        self.game_launch_dialog.close()
                    show_error_dialog(self.master, self.tr("Binary Not Found"), self.tr("The previously selected game binary was not found:\n{}\n\nPlease select a new binary.").format(binary_path))
                    return False
                
                if not os.access(binary_path, os.R_OK):
                    logger.warning(f"Selected binary is not readable: {binary_path}")
                    if self.game_launch_dialog:
                        self.game_launch_dialog.close()
                    show_error_dialog(self.master, self.tr("Permission Error"), self.tr("The selected game binary is not readable:\n{}\n\nPlease check the file permissions.").format(binary_path))
                    return False
                
                if not os.access(binary_path, os.X_OK) and not sys.platform.startswith('win'):
                    logger.warning(f"Selected binary is not executable: {binary_path}")
                    if self.game_launch_dialog:
                        self.game_launch_dialog.close()
                    show_error_dialog(self.master, self.tr("Permission Error"), self.tr("The selected game binary is not executable:\n{}\n\nPlease check the file permissions.").format(binary_path))
                    return False
                
                logger.info(f"Selected binary is valid: {binary_path}")
                return True
            except Exception as e:
                logger.error(f"Error validating binary: {e}")
                show_error_dialog(
                    self.master,
                    self.tr("Validation Error"),
                    self.tr("An error occurred while validating the game binary:\n{}\n\nPlease try selecting the binary again.").format(e)
                )
                return False
        else:
            logger.info("No binary currently selected")
            return False
    
    def execute_selected_binary(self):
        if not self.config.selected_binary:
            logger.warning("No binary selected for execution")
            if self.game_launch_dialog:
                self.game_launch_dialog.close()
            show_error_dialog(self.master, self.tr("Execution Error"), self.tr("No game binary has been selected. Please select a binary first."))
            return
        
        logger.info(f"Should clear cache on launch: {self.config.clear_cache_on_launch}")
        if self.config.clear_cache_on_launch:
            logger.info("Clearing cache before launching game")
            result_kind, message = clear_cache(self.config.game_install_dir)
            if result_kind == "success":
                logger.info("Cache cleared successfully")
            elif result_kind == "warning":
                error_message = self.tr("Cache already empty: {}").format(message)
                logger.warning(error_message)
                if self.game_launch_dialog:
                    self.game_launch_dialog.close()
                show_error_dialog(self.master, self.tr("Cache Clear Warning"), error_message)
            elif result_kind == "error":
                error_message = self.tr("Failed to clear cache: {}").format(message)
                logger.error(error_message)
                if self.game_launch_dialog:
                    self.game_launch_dialog.close()
                show_error_dialog(self.master, self.tr("Cache Clear Error"), error_message)
                return

        binary_path = Path(self.config.selected_binary)
        
        try:
            logger.info(f"Attempting to execute: {binary_path}")
            
            if not binary_path.exists():
                raise FileNotFoundError(f"The selected binary does not exist: {binary_path}")
            
            if not os.access(binary_path, os.R_OK):
                raise PermissionError(f"The selected binary is not readable: {binary_path}")
            
            if not os.access(binary_path, os.X_OK) and not sys.platform.startswith('win'):
                raise PermissionError(f"The selected binary is not executable: {binary_path}")
            
            # Create and show the GameLaunchDialog
            self.game_launch_dialog = GameLaunchDialog(self.master)
            self.game_launch_dialog.show()

            # Start the subprocess
            command = [str(binary_path)]
            logger.debug(f"Prepared command: {command}")
            
            self.game_process = subprocess.Popen(
                command,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=binary_path.parent
            )

            # Check if the process was created successfully
            if self.game_process.pid is None:
                raise RuntimeError("Failed to get process ID after creation")

            # Start monitoring the process
            self.process_monitor_timer.start(1000)  # Check every second
            
            logger.info(f"Binary execution initiated successfully. PID: {self.game_process.pid}")
            
            # Minimize the launcher window if the setting is enabled
            if self.config.minimize_on_launch:
                self.master.showMinimized()
        except Exception as e:
            error_message = self.tr("Failed to execute the selected binary: {}").format(str(e))
            logger.error(error_message, exc_info=True)
            if self.game_launch_dialog:
                self.game_launch_dialog.close()
            show_error_dialog(self.master, self.tr("Execution Error"), error_message)
    
    @Slot(str)
    def on_binary_selected(self, selected_binary):
        self.config.select_binary = selected_binary
        logger.info(f"Selected binary: {selected_binary}")
        self.play_button_clicked.emit()
    
    def open_binary_selection_dialog(self):
        dialog = BinarySelectionDialog(self.config, self.master)
        dialog.binary_selected.connect(self.on_binary_selected)
        dialog.exec()