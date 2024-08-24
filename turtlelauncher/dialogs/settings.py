from turtlelauncher.dialogs.base import BaseDialog
from PySide6.QtWidgets import QWidget, QVBoxLayout, QDialog
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from loguru import logger
from turtlelauncher.utils.config import TOOL_FOLDER, IMAGES
from turtlelauncher.dialogs.binary_select import BinarySelectionDialog
from turtlelauncher.dialogs.generic_confirmation import GenericConfirmationDialog
from pathlib import Path
import os
import shutil


class SettingsDialog(BaseDialog):
    particles_setting_changed = Signal(bool)
    transparency_setting_changed = Signal(bool)
    minimize_on_launch_changed = Signal(bool)

    def __init__(self, parent=None, game_installed=False, config=None):
        icon_path = IMAGES / "turtle_wow_icon.png"
        self.game_installed = game_installed
        self.config = config
        super().__init__(
            parent=parent,
            title="Turtle WoW Settings",
            message="",
            icon_path=str(icon_path),
            modal=True,
            flags=Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.finished.connect(self.on_dialog_finished)

    def setup_ui(self, title, message, icon_path):
        super().setup_ui(title, message, icon_path)
        tab_widget = self.create_tab_widget()

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
        self.create_checkbox("Disable Particles", "particles_disabled", self.config.particles_disabled, launcher_layout)
        self.create_checkbox("Clear Cache On Launch", "clear_cache_on_launch", False, launcher_layout)
        self.create_checkbox("Minimize Launcher on Game Launch", "minimize_on_launch", self.config.minimize_on_launch, launcher_layout)
        # TODO implement transparency toggling
        #self.create_checkbox("Disable Transparency", "transparency_disabled", self.config.transparency_disabled, launcher_layout)
        self.create_button("Open Logs Folder", self.open_logs_folder, launcher_layout)
        tab_widget.addTab(launcher_tab, "Launcher")
        
        # Fixes Tab
        fixes_tab = QWidget()
        fixes_layout = QVBoxLayout(fixes_tab)
        fixes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.create_checkbox("Fix Black Screen", "black_screen_fix", False, fixes_layout)
        self.create_checkbox("Fix VanillaTweaks Alt-Tab", "vanilla_tweaks_alt_tab_fix", False, fixes_layout)
        tab_widget.addTab(fixes_tab, "Fixes")

        self.update_button_states()

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
                if not any(wtf_path.iterdir()):
                    logger.warning("WTF folder is empty")
                    self.show_warning_dialog("Warning", "The WTF folder is already empty. No addon settings to clear.")
                    return

                try:
                    for item in wtf_path.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    logger.info("Successfully cleared addon settings")
                    self.show_success_dialog("Success", "Addon settings have been cleared successfully.")
                except Exception as e:
                    logger.error(f"Error clearing addon settings: {str(e)}")
                    self.show_error_dialog("Error", f"An error occurred while clearing addon settings: {str(e)}")
            else:
                logger.warning("WTF folder not found in the game installation directory")
                self.show_warning_dialog("Warning", "WTF folder not found in the game installation directory.")
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
                if not any(wdb_path.iterdir()):
                    logger.warning("WDB folder is empty")
                    self.show_warning_dialog("Warning", "The cache (WDB folder) is already empty. No cache to clear.")
                    return

                try:
                    for item in wdb_path.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    logger.info("Successfully cleared cache")
                    self.show_success_dialog("Success", "Cache has been cleared successfully.")
                except Exception as e:
                    logger.error(f"Error clearing cache: {str(e)}")
                    self.show_error_dialog("Error", f"An error occurred while clearing cache: {str(e)}")
            else:
                logger.warning("WDB folder not found in the game installation directory")
                self.show_warning_dialog("Warning", "WDB folder (cache) not found in the game installation directory.")
        else:
            logger.debug("Cache clearing cancelled by user")

    def open_install_directory(self):
        logger.debug("Opening install directory")
        if self.config.game_install_dir and os.path.exists(self.config.game_install_dir):
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            os.startfile(self.config.game_install_dir)
            QTimer.singleShot(100, self.restore_top_hint)
        else:
            logger.error("Game install directory not found or doesn't exist")
    
    def restore_top_hint(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.show()

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
            self.show_error_dialog("Error", f"An error occurred while opening the logs folder: {str(e)}")
    
    def fix_black_screen(self):
        logger.debug("Fixing black screen")
        self.show_warning_dialog("Not Implemented", "This feature is not implemented yet.")

    def fix_vanilla_tweaks_alt_tab(self):
        logger.debug("Fixing VanillaTweaks Alt-Tab")
        self.show_warning_dialog("Not Implemented", "This feature is not implemented yet.")
    
    def sizeHint(self):
        return QSize(400, 500) # Set the initial size of the dialog

    def showEvent(self, event):
        super().showEvent(event)
        self.set_setting("particles_disabled", self.config.particles_disabled)
        self.set_setting("transparency_disabled", self.config.transparency_disabled)
        self.adjustSize()  # Adjust the size of the dialog to fit its contents

    def on_dialog_finished(self, result):
        logger.debug("SettingsDialog is finishing, saving settings...")
        self.save_settings()
    
    def on_checkbox_changed(self, setting_name, state):
        super().on_checkbox_changed(setting_name, state)
        logger.info(f"Checkbox changed: {setting_name}, {'True' if state else 'False'}")
        if setting_name == "particles_disabled":
            self.particles_setting_changed.emit(not state)
        elif setting_name == "transparency_disabled":
            self.transparency_setting_changed.emit(state)
        elif setting_name == "minimize_on_launch":
            self.minimize_on_launch_changed.emit(state)

    def save_settings(self):
        particles_checked = self.get_setting("particles_disabled")
        transparency_checked = self.get_setting("transparency_disabled")
        minimize_on_launch_checked = self.get_setting("minimize_on_launch")

        if particles_checked != self.config.particles_disabled:
            logger.debug(f"Saving particles setting: {particles_checked}")
            self.config.particles_disabled = particles_checked
            self.particles_setting_changed.emit(not particles_checked)

        if transparency_checked != self.config.transparency_disabled:
            logger.debug(f"Saving transparency setting: {transparency_checked}")
            self.config.transparency_disabled = transparency_checked
            self.transparency_setting_changed.emit(transparency_checked)

        if minimize_on_launch_checked != self.config.minimize_on_launch:
            logger.debug(f"Saving minimize on launch setting: {minimize_on_launch_checked}")
            self.config.minimize_on_launch = minimize_on_launch_checked
            self.minimize_on_launch_changed.emit(minimize_on_launch_checked)

        self.config.save()
        logger.info("Settings saved successfully")

    def show_warning_dialog(self, title, message):
        custom_styles = {
            "#content-widget": {
                "border": "2px solid #FF8C00"
            }
        }
        GenericConfirmationDialog(
            self, title=title, message=message, confirm_text="OK", cancel_text="",
            icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
            custom_styles=custom_styles
        ).exec()

    def show_success_dialog(self, title, message):
        custom_styles = {
            "#content-widget": {
                "border": "2px solid #45a049"
            }
        }
        GenericConfirmationDialog(
            self, title=title, message=message, confirm_text="OK", cancel_text="",
            icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
            custom_styles=custom_styles
        ).exec()

    def show_error_dialog(self, title, message):
        custom_styles = {
            "#content-widget": {
                "border": "2px solid #F44336"
            }
        }
        GenericConfirmationDialog(
            self, title=title, message=message, confirm_text="OK", cancel_text="",
            icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
            custom_styles=custom_styles
        ).exec()