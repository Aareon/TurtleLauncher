from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, 
                               QCheckBox, QHBoxLayout)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPoint, Signal, QTimer
from loguru import logger
from turtlelauncher.dialogs.binary_select import BinarySelectionDialog
from turtlelauncher.dialogs.generic_confirmation import GenericConfirmationDialog
from turtlelauncher.widgets.tabs import CustomTabWidget
from pathlib import Path
import os
import shutil

USER_DOCUMENTS = Path.home() / "Documents"
TOOL_FOLDER = USER_DOCUMENTS / "TurtleLauncher"
if not TOOL_FOLDER.exists():
    TOOL_FOLDER.mkdir(parents=True)


class SettingsDialog(QDialog):
    particles_setting_changed = Signal(bool)
    transparency_setting_changed = Signal(bool)

    def __init__(self, parent=None, game_installed=False, config=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Turtle WoW Settings")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.game_installed = game_installed
        self.config = config

        self.dragging = False
        self.drag_position = QPoint()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        content_widget = QWidget(self)
        content_widget.setObjectName("content-widget")
        content_layout = QVBoxLayout(content_widget)

        # Logo
        logo = QLabel(content_widget)
        logo_path = Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png"
        if logo_path.exists():
            logo_pixmap = QPixmap(str(logo_path)).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo)

        # Title
        title = QLabel("Turtle WoW Settings", content_widget)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title-label")
        content_layout.addWidget(title)

        # Custom Tabs
        tab_widget = CustomTabWidget(content_widget)
        tab_widget.setObjectName("tab-widget")

        # Game Tab
        game_tab = QWidget()
        game_layout = QVBoxLayout(game_tab)
        game_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.clear_addon_settings_button = self.create_button("Clear Addon Settings", self.clear_addon_settings, game_layout)
        self.clear_cache_button = self.create_button("Clear Cache", self.clear_cache, game_layout)
        self.open_install_directory_button = self.create_button("Open Install Directory", self.open_install_directory, game_layout)
        self.select_binary_button = self.create_button("Select Binary to Launch", self.select_binary, game_layout)
        tab_widget.addTab(game_tab, "Game")

        # Launcher Tab
        launcher_tab = QWidget()
        launcher_layout = QVBoxLayout(launcher_tab)
        launcher_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.particles_checkbox = QCheckBox("Disable Particles", self)
        self.particles_checkbox.setObjectName("settings-checkbox")
        self.particles_checkbox.setChecked(self.config.particles_disabled)
        self.particles_checkbox.stateChanged.connect(self.on_particles_checkbox_changed)
        launcher_layout.addWidget(self.particles_checkbox)

        self.transparency_checkbox = QCheckBox("Disable Transparency", self)
        self.transparency_checkbox.setObjectName("settings-checkbox")
        self.transparency_checkbox.setChecked(self.config.transparency_disabled)
        launcher_layout.addWidget(self.transparency_checkbox)

        self.open_logs_folder_button = self.create_button("Open Logs Folder", self.open_logs_folder, launcher_layout)
        tab_widget.addTab(launcher_tab, "Launcher")

        content_layout.addWidget(tab_widget)

        # Close button
        close_button = QPushButton("×", content_widget)
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.close)

        # Add close button to top-right corner
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(close_button)
        content_layout.insertLayout(0, top_layout)

        layout.addWidget(content_widget)

        self.setStyleSheet("""
            #content-widget {
                background-color: rgba(44, 47, 51, 230);
                border: 2px solid #7289DA;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            #title-label {
                font-size: 18px;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton {
                background-color: #7289DA;
                color: white;
                border: none;
                padding: 10px;
                margin: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5B6EAE;
            }
            QPushButton:disabled {
                background-color: #4A5162;
                color: #8E9297;
            }
            #close-button {
                background-color: transparent;
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin: 5px;
                padding: 0;
            }
            #close-button:hover {
                color: #FF5555;
            }
            #settings-checkbox {
                color: white;
                font-size: 14px;
                padding: 5px 0;
            }
            #settings-checkbox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #7289DA;
                border-radius: 4px;
                background-color: #2C2F33;
            }
            #settings-checkbox::indicator:checked {
                background-color: #7289DA;
                image: url(check.png);
            }
            #settings-checkbox::indicator:hover {
                border-color: #5B6EAE;
            }
            #tab-widget {
                background-color: transparent;
                border: none;
            }
        """)

    def create_button(self, text, function, layout):
        button = QPushButton(text, self)
        button.clicked.connect(function)
        layout.addWidget(button)
        return button

    def update_button_states(self):
        buttons = [
            self.clear_addon_settings_button,
            self.clear_cache_button,
            self.open_install_directory_button,
            self.select_binary_button
        ]
        for button in buttons:
            button.setEnabled(self.game_installed)

    def clear_addon_settings(self):
        custom_styles = {
            "#message-label-0": {
                "color": "#FFD700"
            },
            "#message-label-1": {
                "color": "#FF69B4"
            }
        }
        
        confirmation_dialog = GenericConfirmationDialog(
            self,
            title="Confirm Action",
            message=[
                "Are you sure you want to clear all addon settings?",
                "This action cannot be undone."
            ],
            confirm_text="Yes, clear",
            cancel_text="No, cancel",
            icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
            custom_styles=custom_styles
        )
        
        if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
            logger.debug("Clearing addon settings")
            wtf_path = Path(self.config.game_install_dir) / "WTF"
            
            if wtf_path.exists():
                # Check if the WTF folder is empty
                if not any(wtf_path.iterdir()):
                    logger.warning("WTF folder is empty")
                    custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #FF8C00"
                        }
                    }
                    GenericConfirmationDialog(
                        self,
                        title="Warning",
                        message="The WTF folder is already empty. No addon settings to clear.",
                        confirm_text="OK",
                        cancel_text="",
                        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                        custom_styles=custom_styles
                    ).exec()
                    return

                try:
                    for item in wtf_path.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    logger.info("Successfully cleared addon settings")
                    custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #45a049"
                        }
                    }
                    GenericConfirmationDialog(
                        self,
                        title="Success",
                        message="Addon settings have been cleared successfully.",
                        confirm_text="OK",
                        cancel_text="",
                        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                        custom_styles=custom_styles
                    ).exec()
                except Exception as e:
                    logger.error(f"Error clearing addon settings: {str(e)}")
                    custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #F44336"
                        }
                    }
                    GenericConfirmationDialog(
                        self,
                        title="Error",
                        message=f"An error occurred while clearing addon settings: {str(e)}",
                        confirm_text="OK",
                        cancel_text="",
                        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                        custom_styles=custom_styles
                    ).exec()
            else:
                logger.warning("WTF folder not found in the game installation directory")
                custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #FF8C00"
                        }
                    }
                GenericConfirmationDialog(
                    self,
                    title="Warning",
                    message="WTF folder not found in the game installation directory.",
                    confirm_text="OK",
                    cancel_text="",
                    icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                    custom_styles=custom_styles
                ).exec()
        else:
            logger.debug("Addon settings clearing cancelled by user")

    def clear_cache(self):
        logger.debug("Clearing cache")
        
        custom_styles = {
            "#message-label-0": {
                "color": "#FFD700"
            },
            "#message-label-1": {
                "color": "#FF69B4"
            }
        }
        
        confirmation_dialog = GenericConfirmationDialog(
            self,
            title="Confirm Action",
            message=["Are you sure you want to clear the cache?", "This action cannot be undone."],
            confirm_text="Yes, clear",
            cancel_text="No, cancel",
            icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
            custom_styles=custom_styles
        )
        
        if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
            wdb_path = Path(self.config.game_install_dir) / "WDB"
            
            if wdb_path.exists() and wdb_path.is_dir():
                # Check if the WDB folder is empty
                if not any(wdb_path.iterdir()):
                    logger.warning("WDB folder is empty")
                    custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #FF8C00"
                        }
                    }
                    GenericConfirmationDialog(
                        self,
                        title="Warning",
                        message="The cache (WDB folder) is already empty. No cache to clear.",
                        confirm_text="OK",
                        cancel_text="",
                        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                        custom_styles=custom_styles
                    ).exec()
                    return

                try:
                    for item in wdb_path.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    logger.info("Successfully cleared cache")
                    custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #45a049"
                        }
                    }
                    GenericConfirmationDialog(
                        self,
                        title="Success",
                        message="Cache has been cleared successfully.",
                        confirm_text="OK",
                        cancel_text="",
                        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                        custom_styles=custom_styles
                    ).exec()
                except Exception as e:
                    logger.error(f"Error clearing cache: {str(e)}")
                    custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #F44336"
                        }
                    }
                    GenericConfirmationDialog(
                        self,
                        title="Error",
                        message=f"An error occurred while clearing cache: {str(e)}",
                        confirm_text="OK",
                        cancel_text="",
                        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                        custom_styles=custom_styles
                    ).exec()
            else:
                logger.warning("WDB folder not found in the game installation directory")
                custom_styles = {
                        "#content-widget": {
                            "border": "2px solid #FF8C00"
                        }
                    }
                GenericConfirmationDialog(
                    self,
                    title="Warning",
                    message="WDB folder (cache) not found in the game installation directory.",
                    confirm_text="OK",
                    cancel_text="",
                    icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                    custom_styles=custom_styles
                ).exec()
        else:
            logger.debug("Cache clearing cancelled by user")

    def open_install_directory(self):
        logger.debug("Opening install directory")
        if self.config.game_install_dir and os.path.exists(self.config.game_install_dir):
            # Remove the WindowStaysOnTopHint flag
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()  # Need to call show() after changing flags

            # Open the directory
            os.startfile(self.config.game_install_dir)

            # Use a timer to restore the flag after a short delay
            QTimer.singleShot(100, self.restore_top_hint)
        else:
            logger.error("Game install directory not found or doesn't exist")
    
    def restore_top_hint(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.show()  # Need to call show() after changing flags

    def select_binary(self):
        binary_dialog = BinarySelectionDialog(self.config, self)
        if binary_dialog.exec() == QDialog.DialogCode.Accepted:
            logger.debug("Binary selected from custom dialog")

    def open_logs_folder(self):
        logger.debug("Opening logs folder")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

        logs_folder = TOOL_FOLDER / "logs"
        
        if not logs_folder.exists():
            logger.warning(f"Logs folder does not exist: {logs_folder}")
            logs_folder.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created logs folder: {logs_folder}")

        try:
            os.startfile(str(logs_folder))
            logger.info(f"Opened logs folder: {logs_folder}")
            QTimer.singleShot(100, self.restore_top_hint)
        except Exception as e:
            logger.error(f"Error opening logs folder: {str(e)}")
            custom_styles = {
                "#content-widget": {
                    "border": "2px solid #F44336"
                }
            }
            GenericConfirmationDialog(
                self,
                title="Error",
                message=f"An error occurred while opening the logs folder: {str(e)}",
                confirm_text="OK",
                cancel_text="",
                icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
                custom_styles=custom_styles
            ).exec()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        # Update checkbox states when dialog is shown
        self.particles_checkbox.setChecked(self.config.particles_disabled)
        self.transparency_checkbox.setChecked(self.config.transparency_disabled)

    def closeEvent(self, event):
        # Save the settings when the dialog is closed
        self.save_settings()
        super().closeEvent(event)
    
    def on_particles_checkbox_changed(self, state):
        particles_disabled = state == Qt.CheckState.Checked.value
        logger.debug(f"Particles checkbox changed: disabled = {particles_disabled}")
        self.particles_setting_changed.emit(not particles_disabled)  # Emit True if particles are enabled

    def save_settings(self):
        particles_checked = self.particles_checkbox.isChecked()
        transparency_checked = self.transparency_checkbox.isChecked()

        if particles_checked != self.config.particles_disabled:
            logger.debug(f"Saving particles setting: {particles_checked}")
            self.config.particles_disabled = particles_checked
            self.particles_setting_changed.emit(not particles_checked)  # Emit True if particles are enabled

        if transparency_checked != self.config.transparency_disabled:
            logger.debug(f"Saving transparency setting: {transparency_checked}")
            self.config.transparency_disabled = transparency_checked
            self.transparency_setting_changed.emit(transparency_checked)

        self.config.save()