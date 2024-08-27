from turtlelauncher.dialogs.base import BaseDialog
from PySide6.QtWidgets import QProgressBar, QLabel
from PySide6.QtCore import Qt, QTimer
from loguru import logger
from turtlelauncher.utils.globals import IMAGES

class GameLaunchDialog(BaseDialog):
    def __init__(self, parent=None):
        self.master = parent
        icon_path = IMAGES / "turtle_wow_icon.png"
        super().__init__(
            parent=parent,
            title="Game Running",
            message="",
            icon_path=str(icon_path),
            modal=False,
            flags=Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )

        # Initialize debug_timer
        self.debug_timer = QTimer(self)
        self.debug_timer.timeout.connect(self.debug_visibility)
        self.debug_timer.start(1000)  # Check every second

    def setup_ui(self, title, message, icon_path):
        super().setup_ui(title, message, icon_path)
        
        # Progress Bar
        self.progress_bar = QProgressBar(self.content_widget)
        self.progress_bar.setRange(0, 0)  # This makes the progress bar indeterminate
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName("progress-bar")
        self.content_layout.addWidget(self.progress_bar)

        # Status Message
        self.status_label = QLabel(self.tr("Game is running..."), self.content_widget)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("status-label")
        self.status_label.setWordWrap(True)
        self.content_layout.addWidget(self.status_label)

        # Ensure the dialog has a minimum size
        self.setMinimumSize(300, 200)

    def generate_stylesheet(self, custom_styles=None):
        base_stylesheet = super().generate_stylesheet(custom_styles)
        additional_styles = """
            #progress-bar {
                background-color: #2C2F33;
                border: 1px solid #7289DA;
                border-radius: 5px;
                height: 20px;
            }
            #progress-bar::chunk {
                background-color: #7289DA;
                border-radius: 5px;
            }
        """
        return base_stylesheet + additional_styles

    def debug_visibility(self):
        logger.debug(f"GameLaunchDialog visibility: {self.isVisible()}, Geometry: {self.geometry()}")
        parent = self.master
        if parent is not None:
            logger.debug(f"Parent geometry: {parent.geometry()}")
        else:
            logger.debug("No parent widget")

    def closeEvent(self, event):
        logger.info("GameLaunchDialog closeEvent triggered")
        self.debug_timer.stop()
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_parent()
