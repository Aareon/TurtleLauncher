from turtlelauncher.dialogs.base import BaseDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class ErrorDialog(BaseDialog):
    def __init__(self, parent=None, title="Error", message=""):
        super().__init__(
            parent=parent,
            title=title,
            message=message,
            modal=True,
            flags=Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.update_translations()

    def setup_ui(self, title, message, icon_path):
        super().setup_ui(title, message, icon_path)

        # Add OK button
        self.ok_button = QPushButton(self.content_widget)
        self.ok_button.setObjectName("ok-button")
        self.ok_button.clicked.connect(self.accept)
        self.content_layout.addWidget(self.ok_button)
    
    def update_translations(self):
        self.setWindowTitle(self.tr("Error"))
        self.ok_button.setText(self.tr("OK"))

    def generate_stylesheet(self, custom_styles=None):
        base_stylesheet = super().generate_stylesheet(custom_styles)
        additional_styles = """
            #content-widget {
                border: 2px solid #F44336;
            }
            #ok-button {
                background-color: #F44336;
            }
            #ok-button:hover {
                background-color: #D32F2F;
            }
        """
        return base_stylesheet + additional_styles

    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_parent()