from loguru import logger
from turtlelauncher.dialogs.base import BaseDialog
from turtlelauncher.utils.globals import IMAGES
from PySide6.QtWidgets import QLabel


class FirstLaunchDialog(BaseDialog):
    CLOSED = 2  # Custom result code

    def __init__(self, parent=None):
        super().__init__(
            parent,
            icon_path=IMAGES / "turtle_wow_icon.png"
        )
        logger.debug("Initializing FirstLaunchDialog")

        self.setup_message_label()
        self.setup_buttons()
        self.update_translations()

    def setup_message_label(self):
        self.message_label = QLabel(self.content_widget)
        self.message_label.setObjectName("message-label")
        self.content_layout.addWidget(self.message_label)

    def setup_buttons(self):
        self.select_button = self.create_button("", self.accept, self.content_layout, "select-button")
        self.download_button = self.create_button("", self.reject, self.content_layout, "download-button")

    def update_translations(self):
        self.setWindowTitle(self.tr("Turtle WoW Launcher Setup"))
        self.message_label.setText(self.tr("Choose how you want to set up the game:"))
        self.select_button.setText(self.tr("Select existing installation"))
        self.download_button.setText(self.tr("Download game"))

    def handle_close(self):
        logger.debug("FirstLaunchDialog close button clicked")
        self.done(self.CLOSED)

    def closeEvent(self, event):
        logger.debug("FirstLaunchDialog close event triggered")
        self.done(self.CLOSED)
        super().closeEvent(event)

    def generate_stylesheet(self, custom_styles=None):
        base_stylesheet = super().generate_stylesheet(custom_styles)
        additional_styles = """
            #message-label {
                color: white;
                font-size: 16px;
                margin-bottom: 15px;
            }
            #select-button, #download-button {
                margin-top: 10px;
            }
        """
        return base_stylesheet + additional_styles