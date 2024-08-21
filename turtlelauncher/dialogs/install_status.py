from pathlib import Path
from turtlelauncher.dialogs.base import BaseDialog
from turtlelauncher.utils.config import IMAGES


class InstallationStatusDialog(BaseDialog):
    def __init__(self, parent=None, status="success", message=""):
        icon_path = IMAGES / "turtle_wow_icon.png"
        title = "Installation Complete" if status == "success" else "Installation Status"
        self.status = status
        super().__init__(parent, title=title, message=message, icon_path=icon_path)

        self.add_ok_button()
        self.apply_status_styles()

    def add_ok_button(self):
        # OK button
        self.ok_button = self.create_button("OK", self.accept, self.content_layout, "ok-button")

    def apply_status_styles(self):
        status_color = self.get_status_color()
        hover_color = self.get_hover_color()

        custom_styles = {
            "#content-widget": {
                "border": f"2px solid {status_color}"
            },
            "QPushButton": {
                "background-color": status_color
            },
            "QPushButton:hover": {
                "background-color": hover_color
            }
        }

        self.setStyleSheet(self.generate_stylesheet(custom_styles))

    def get_status_color(self):
        return {
            "success": "#4CAF50",
            "warning": "#FFA500",
            "error": "#F44336"
        }.get(self.status, "#7289DA")

    def get_hover_color(self):
        return {
            "success": "#45a049",
            "warning": "#FF8C00",
            "error": "#D32F2F"
        }.get(self.status, "#5B6EAE")