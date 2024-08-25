from loguru import logger
from turtlelauncher.dialogs.base import BaseDialog
from turtlelauncher.utils.globals import IMAGES


class FirstLaunchDialog(BaseDialog):
    CLOSED = 2  # Custom result code

    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="Turtle WoW Launcher Setup",
            message="Choose how you want to set up the game:",
            icon_path=IMAGES / "turtle_wow_icon.png"
        )
        logger.debug("Initializing FirstLaunchDialog")

        self.setup_buttons()

    def setup_buttons(self):
        select_button = self.create_button("Select existing installation", self.accept, self.content_layout, "select-button")  # noqa: F841
        download_button = self.create_button("Download game", self.reject, self.content_layout, "download-button")  # noqa: F841

    def handle_close(self):
        logger.debug("FirstLaunchDialog close button clicked")
        self.done(self.CLOSED)

    def closeEvent(self, event):
        logger.debug("FirstLaunchDialog close event triggered")
        self.done(self.CLOSED)
        super().closeEvent(event)
        logger.debug("FirstLaunchDialog close event triggered")
        self.done(self.CLOSED)
        super().closeEvent(event)