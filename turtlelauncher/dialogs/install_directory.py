from PySide6.QtWidgets import QLabel, QFileDialog
from PySide6.QtCore import Qt
from pathlib import Path
from loguru import logger
from turtlelauncher.dialogs.base import BaseDialog


class InstallationDirectoryDialog(BaseDialog):
    def __init__(self, parent=None, is_existing_install=False):
        title = "Choose Installation Directory"
        message = "Select where Turtle WoW is installed:" if is_existing_install else "Choose where you want to install Turtle WoW:"
        icon_path = Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png"
        
        super().__init__(parent, title, message, icon_path)
        
        self.is_existing_install = is_existing_install
        self.selected_directory = None

        self.setup_additional_ui()

    def setup_additional_ui(self):
        # Selected directory label
        self.selected_dir_label = QLabel("No directory selected", self.content_widget)
        self.selected_dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_dir_label.setObjectName("selected-dir-label")
        self.selected_dir_label.setWordWrap(True)
        self.content_layout.addWidget(self.selected_dir_label)

        # Select directory button
        select_button = self.create_button("Select Directory", self.select_directory, self.content_layout, "select-button")

        # Confirm button
        self.confirm_button = self.create_button("Confirm", self.accept, self.content_layout, "confirm-button")
        self.confirm_button.setEnabled(False)  # Initially disable the Confirm button

    def select_directory(self):
        dialog_title = "Select Existing Turtle WoW Directory" if self.is_existing_install else "Select Installation Directory"
        directory = QFileDialog.getExistingDirectory(self, dialog_title)
        if directory:
            self.selected_directory = directory
            self.selected_dir_label.setText(f"Selected: {directory}")
            self.confirm_button.setEnabled(True)  # Enable the Confirm button after directory selection
            logger.debug(f"Selected {'existing' if self.is_existing_install else 'installation'} directory: {directory}")

    def generate_stylesheet(self, custom_styles=None):
        base_stylesheet = super().generate_stylesheet(custom_styles)
        additional_styles = """
            #selected-dir-label {
                font-size: 12px;
                color: #BBBBBB;
                margin: 5px 0;
            }
            #confirm-button:disabled {
                background-color: #4A4A4A;
                color: #8A8A8A;
            }
        """
        return base_stylesheet + additional_styles