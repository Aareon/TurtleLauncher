from PySide6.QtWidgets import QLabel, QFileDialog
from PySide6.QtCore import Qt
from pathlib import Path
from loguru import logger
from turtlelauncher.dialogs.base import BaseDialog
from turtlelauncher.dialogs.generic_confirmation import GenericConfirmationDialog
import os

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
            logger.info(f"Selected directory: {directory}")
            if not self.has_directory_permissions(directory):
                if self.confirm_privileged_directory(directory):
                    self.set_selected_directory(directory)
                else:
                    logger.info("User cancelled privileged directory selection")
            else:
                self.set_selected_directory(directory)

    def has_directory_permissions(self, directory):
        logger.info(f"Checking permissions for directory: {directory}")
        try:
            # Check read permission
            logger.debug("Checking read permission...")
            os.listdir(directory)
            logger.debug("Read permission check passed")
            
            # Check write permission
            logger.debug("Checking write permission...")
            test_file = os.path.join(directory, 'test_write_permission.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.debug("Write permission check passed")
            
            # Check execute permission
            logger.debug("Checking execute permission...")
            original_dir = os.getcwd()
            os.chdir(directory)
            os.chdir(original_dir)  # Change back to original directory
            logger.debug("Execute permission check passed")
            
            logger.info(f"All permission checks passed for directory: {directory}")
            return True
        except PermissionError as pe:
            logger.error(f"Permission error encountered: {pe}")
            return False
        except OSError as ose:
            logger.error(f"OS error encountered: {ose}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during permission check: {e}")
            return False

    def confirm_privileged_directory(self, directory):
        logger.debug(f"Confirming privileged directory: {directory}")
        confirmation_dialog = GenericConfirmationDialog(
            self,
            title="Warning: Limited Permissions",
            message=f"You may have limited permissions in the selected directory: {directory}\n\nThe application might not function correctly without full read, write, and execute permissions. Do you want to proceed?",
            confirm_text="Yes, I understand",
            cancel_text="No, I want to choose another directory",
            icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
        )
        result = confirmation_dialog.exec() == GenericConfirmationDialog.Accepted
        logger.debug(f"Privileged directory confirmation result: {result}")
        return result

    def set_selected_directory(self, directory):
        self.selected_directory = directory
        self.selected_dir_label.setText(f"Selected: {directory}")
        self.confirm_button.setEnabled(True)
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