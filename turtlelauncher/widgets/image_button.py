from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPixmap, QFont, QPainter
from pathlib import Path

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"
DATA = HERE / "data"
IMAGES = ASSETS / "images"


class ImageButton(QPushButton):
    def __init__(self, image_filename, text, font_name, parent=None):
        super().__init__(text, parent)
        self.font_name = font_name
        self.image_filename = image_filename

        self.setFixedSize(120, 40)
        self.setText(text)
        self.setFont(QFont(self.font_name, 12))
        self.setStyleSheet("""
            QPushButton {
                border: none;
                color: #ffd700; /* #ffd700 or #B2E4E9 */
                text-align: center;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(IMAGES / self.image_filename)
        painter.drawPixmap(self.rect(), pixmap)
        super().paintEvent(event)