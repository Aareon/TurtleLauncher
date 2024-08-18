from PySide6.QtGui import QPixmap, QCursor, QDesktopServices
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QUrl
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class IconButton(QLabel):
    def __init__(self, image_path, url, size=32):
        super().__init__()
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            logger.error(f"Failed to load image: {image_path}")
        else:
            self.setPixmap(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.url = url
        self.setFixedSize(size, size)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            QDesktopServices.openUrl(QUrl(self.url))