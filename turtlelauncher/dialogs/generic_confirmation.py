from turtlelauncher.dialogs.base import BaseDialog
from PySide6.QtWidgets import QHBoxLayout

class GenericConfirmationDialog(BaseDialog):
    def __init__(self, parent=None, title="Confirmation", message="", confirm_text="OK", cancel_text="Cancel", icon_path=None, custom_styles=None):
        super().__init__(parent, title, message, icon_path, custom_styles)

        self.setup_buttons(confirm_text, cancel_text)

    def setup_buttons(self, confirm_text, cancel_text):
        button_layout = QHBoxLayout()
        
        self.confirm_button = self.create_button(confirm_text, self.accept, button_layout, "confirm-button")
        
        if cancel_text:
            self.cancel_button = self.create_button(cancel_text, self.reject, button_layout, "cancel-button")

        self.content_layout.addLayout(button_layout)