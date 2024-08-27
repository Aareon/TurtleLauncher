from PySide6.QtWidgets import QHBoxLayout
from turtlelauncher.dialogs.base import BaseDialog
from loguru import logger
from turtlelauncher.utils.globals import IMAGES


class StopDownloadDialog(BaseDialog):
    def __init__(self, parent=None):
        icon_path = IMAGES / "turtle_wow_icon.png"
        super().__init__(
            parent=parent,
            title=self.tr("Stop Download"),
            icon_path=icon_path,
            modal=True,
            custom_styles=self.get_custom_styles()
        )

        self.add_message(self.tr("Are you sure you want to stop the download?"), color="#FFD700")  # Gold color
        self.add_message(self.tr("The download progress will be lost."), color="#FF69B4")  # Hot pink color

        self.setup_buttons()

    def setup_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.create_button(self.tr("Yes, Stop"), self.accept, button_layout, "dialog-button")
        self.create_button(self.tr("No, Continue"), self.reject, button_layout, "dialog-button")

        self.content_layout.addLayout(button_layout)

    def get_custom_styles(self):
        return {
            "#warning-label": {
                "color": "#FFD700",
                "font-size": "16px",
                "margin": "10px 0"
            },
            "#info-label": {
                "color": "#FF69B4",
                "font-size": "14px",
                "margin": "5px 0"
            }
        }

    def showEvent(self, event):
        super().showEvent(event)
        # Must translate for check, as the button text was likely translated
        if self.tr("Yes, Stop") in self.buttons:
            self.buttons[self.tr("Yes, Stop")].setFocus()
        else:
            logger.warning("'Yes, Stop' button not found in buttons dictionary")