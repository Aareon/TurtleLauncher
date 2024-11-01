from turtlelauncher.dialogs.base import BaseDialog
from PySide6.QtWidgets import QWidget, QVBoxLayout, QDialog, QLabel, QComboBox, QTabWidget
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from loguru import logger
from turtlelauncher.utils.globals import TOOL_FOLDER, IMAGES
from turtlelauncher.utils.game_utils import clear_cache
from turtlelauncher.dialogs.binary_select import BinarySelectionDialog
from turtlelauncher.dialogs.generic_confirmation import GenericConfirmationDialog
from turtlelauncher.dialogs import show_error_dialog, show_success_dialog, show_warning_dialog
from turtlelauncher.utils.fixes import vanilla_tweaks, base_fixes
from turtlelauncher.utils.errors import ResultKind
import os


class SettingsDialog(BaseDialog):
    particles_setting_changed = Signal(bool)
    transparency_setting_changed = Signal(bool)
    minimize_on_launch_changed = Signal(bool)
    clear_cache_on_launch_changed = Signal(bool)
    language_changed = Signal(str)

    def __init__(self, parent=None, game_installed=False, config=None):
        icon_path = IMAGES / "turtle_wow_icon.png"
        self.game_installed = game_installed
        self.config = config
        self.master = parent
        super().__init__(
            parent=self.master,
            title=self.tr("Turtle WoW Settings"),
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
        self.clear_addon_settings_button = self.create_button("", self.clear_addon_settings, game_layout)
        self.clear_cache_button = self.create_button("", self.clear_cache, game_layout)
        self.clear_chat_cache_button = self.create_button("", self.clear_chat_cache, game_layout)
        self.open_install_directory_button = self.create_button("", self.open_install_directory, game_layout)
        self.select_binary_button = self.create_button("", self.select_binary, game_layout)
        tab_widget.addTab(game_tab, "")

        # Launcher Tab
        launcher_tab = QWidget()
        launcher_layout = QVBoxLayout(launcher_tab)
        launcher_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.language_label = QLabel()
        launcher_layout.addWidget(self.language_label)
        self.language_combo = QComboBox()
        available_languages = ["English"]
        self.language_combo.addItems(available_languages)
        
        current_language_index = available_languages.index(self.config.language)
        self.language_combo.setCurrentIndex(current_language_index)
        
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        self.style_combo_box(self.language_combo)
        launcher_layout.addWidget(self.language_combo)
        
        self.particles_checkbox = self.create_checkbox("", "particles_disabled", self.config.particles_disabled, launcher_layout)
        self.clear_cache_checkbox = self.create_checkbox("", "clear_cache_on_launch", self.config.clear_cache_on_launch, launcher_layout)
        self.minimize_checkbox = self.create_checkbox("", "minimize_on_launch", self.config.minimize_on_launch, launcher_layout)
        
        self.open_logs_button = self.create_button("", self.open_logs_folder, launcher_layout)
        tab_widget.addTab(launcher_tab, "")
        
        # Fixes Tab
        fixes_tab = QWidget()
        fixes_layout = QVBoxLayout(fixes_tab)
        fixes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.fix_black_screen_button = self.create_button("", self.fix_black_screen, fixes_layout)
        self.fix_vanilla_tweaks_button = self.create_button("", self.fix_vanilla_tweaks_alt_tab, fixes_layout)
        tab_widget.addTab(fixes_tab, "")

        self.update_button_states()
        self.update_translations()

        self.update_button_states()
    
    def on_language_changed(self, language):
        logger.info(f"Language changed to: {language}")
        self.config.language = language
        self.config.save()
        self.language_changed.emit(language)
        
        # Update the dialog's translations
        self.update_translations()
    
    def update_translations(self):
        self.setWindowTitle(self.tr("Turtle WoW Settings"))
        
        # Update tab titles
        tab_widget = self.findChild(QTabWidget)
        if tab_widget:
            tab_widget.setTabText(0, self.tr("Game"))
            tab_widget.setTabText(1, self.tr("Launcher"))
            tab_widget.setTabText(2, self.tr("Fixes"))
        
        # Update button texts
        self.clear_addon_settings_button.setText(self.tr("Clear Addon Settings"))
        self.clear_cache_button.setText(self.tr("Clear Cache"))
        self.clear_chat_cache_button.setText(self.tr("Clear Chat Cache"))
        self.open_install_directory_button.setText(self.tr("Open Install Directory"))
        self.select_binary_button.setText(self.tr("Select Binary to Launch"))
        self.open_logs_button.setText(self.tr("Open Logs Folder"))
        self.fix_black_screen_button.setText(self.tr("Fix Black Screen"))
        self.fix_vanilla_tweaks_button.setText(self.tr("Fix VanillaTweaks Alt-Tab"))
        
        # Update checkbox texts
        self.particles_checkbox.setText(self.tr("Disable Particles"))
        self.clear_cache_checkbox.setText(self.tr("Clear Cache on Launch"))
        self.minimize_checkbox.setText(self.tr("Minimize Launcher on Game Launch"))
        
        # Update language label
        self.language_label.setText(self.tr("Select Language"))

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
            title=self.tr("Confirm Action"),
            message=[
                self.tr("Are you sure you want to clear all addon settings?"),
                self.tr("This action cannot be undone.")
            ],
            confirm_text=self.tr("Yes, clear"),
            cancel_text=self.tr("No, cancel"),
            icon_path=IMAGES / "turtle_wow_icon.png",
            custom_styles=custom_styles
        )
        
        if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
            logger.debug("Clearing addon settings")
            result_kind, result_message = base_fixes.clear_addon_settings(self.config.game_install_dir)
            if result_kind == ResultKind.WARNING:
                show_warning_dialog(self, self.tr("Warning"), self.tr(result_message))
            elif result_kind == ResultKind.SUCCESS:
                show_success_dialog(self, self.tr("Success"), self.tr(result_message))
            elif result_kind == ResultKind.ERROR:
                show_error_dialog(self, self.tr("Error"), self.tr(result_message))
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
            title=self.tr("Confirm Action"),
            message=[self.tr("Are you sure you want to clear the cache?"), self.tr("This action cannot be undone.")],
            confirm_text=self.tr("Yes, clear"),
            cancel_text=self.tr("No, cancel"),
            icon_path=IMAGES / "turtle_wow_icon.png",
            custom_styles=custom_styles
        )
        
        if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
            kind, message = clear_cache(self.config.game_install_dir)
            if kind == ResultKind.WARNING:
                show_warning_dialog(self, self.tr("Warning"), message)
            elif kind == ResultKind.SUCCESS:
                show_success_dialog(self, self.tr("Success"), message)
            elif kind == ResultKind.ERROR:
                show_error_dialog(self, self.tr("Error"), message)
        else:
            logger.debug("Cache clearing cancelled by user")
    
    def clear_chat_cache(self):
        logger.debug("Clearing chat cache. TODO!")
        return

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
            show_error_dialog("Error", f"An error occurred while opening the logs folder: {str(e)}")
    
    def fix_black_screen(self):
        logger.debug("Fixing black screen")

        kind, message = base_fixes.fix_black_screen(self.config.game_install_dir)
        if kind == ResultKind.ERROR:
            show_error_dialog(self, self.tr("Error"), self.tr(message))
        elif kind == ResultKind.SUCCESS:
            show_success_dialog(self, self.tr("Success"), self.tr(message))
        elif kind == ResultKind.WARNING:
            show_warning_dialog(self, self.tr("Warning"), self.tr(message))
        else:
            logger.warning(f"Unknown result kind: {kind}")

    def fix_vanilla_tweaks_alt_tab(self):
        logger.debug("Fixing VanillaTweaks Alt-Tab")
        kind, message = vanilla_tweaks.fix_alt_tab(self.config.game_install_dir)
        if kind == ResultKind.ERROR:
            show_error_dialog(self, self.tr("Error"), message)
        elif kind == ResultKind.SUCCESS:
            show_success_dialog(self, self.tr("Success"), message)
        elif kind == ResultKind.WARNING:
            show_warning_dialog(self, self.tr("Warning"), message)
    
    def sizeHint(self):
        return QSize(400, 500) # Set the initial size of the dialog

    def style_combo_box(self, combo_box):
        combo_box.setStyleSheet("""
            QComboBox {
                background-color: #2C2F33;
                color: #FFFFFF;
                border: 1px solid #99AAB5;
                padding: 5px;
                border-radius: 3px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #99AAB5;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #7289DA;
            }
            QComboBox::down-arrow {
                image: url(path/to/dropdown_arrow.png);
            }
            QComboBox QAbstractItemView {
                background-color: #2C2F33;
                color: #FFFFFF;
                selection-background-color: #7289DA;
                border: 1px solid #99AAB5;
            }
        """)

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
        elif setting_name == "clear_cache_on_launch":
            self.clear_cache_on_launch_changed.emit(state)

    def save_settings(self):
        particles_checked = self.get_setting("particles_disabled")
        transparency_checked = self.get_setting("transparency_disabled")
        minimize_on_launch_checked = self.get_setting("minimize_on_launch")
        clear_cache_on_launch_checked = self.get_setting("clear_cache_on_launch")

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
        
        if clear_cache_on_launch_checked != self.config.clear_cache_on_launch:
            logger.debug(f"Saving clear cache on launch setting: {clear_cache_on_launch_checked}")
            self.config.clear_cache_on_launch = clear_cache_on_launch_checked
            self.clear_cache_on_launch_changed.emit(clear_cache_on_launch_checked)
        
        if self.language_combo:
            selected_language = self.language_combo.currentText()
            if selected_language != self.config.language:
                logger.debug(f"Saving language setting: {selected_language}")
                self.config.language = selected_language
                self.language_changed.emit(selected_language)

        self.config.save()
        logger.info("Settings saved successfully")
