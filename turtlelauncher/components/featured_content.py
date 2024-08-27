import logging
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QStackedWidget, QSizePolicy
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QFontDatabase
from PySide6.QtCore import Qt, QSize

from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.yt_video import YouTubeVideoWidget
from turtlelauncher.widgets.turtle_tv import TurtleTVWidget
from turtlelauncher.utils.globals import FONTS, IMAGES
from turtlelauncher.utils.config import Config

logger = logging.getLogger(__name__)

class FeaturedContent(QFrame):
    def __init__(self, config: Config, content_type="image", video_data=None, featured_image=None):
        super().__init__()
        self.config = config
        
        self.setFrameStyle(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(400, 300)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Title
        font_filename = "FontinSans_Cyrillic_R_46b.ttf"
        font_id = QFontDatabase.addApplicationFont(str((FONTS / font_filename).absolute()))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        
        self.title = GradientLabel(
            "",
            QColor(255, 215, 0),
            QColor(255, 105, 180),
            intensity=2.0,
            vertical=True
        )
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont(font_family, 16, QFont.Bold))
        self.title.setMaximumHeight(40)
        self.layout.addWidget(self.title)

        # Stacked Widget
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget, 1)

        # Featured Image
        self.featured_image_label = QLabel()
        pixmap = QPixmap(featured_image) if featured_image else QPixmap(IMAGES / "feature_image.png")
        self.featured_image_label.setPixmap(pixmap)
        self.featured_image_label.setScaledContents(True)
        self.featured_image_label.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(self.featured_image_label)

        # Video Widget
        self.video_widget = None
        if content_type == "youtube" and video_data:
            self.video_widget = YouTubeVideoWidget(video_data)
        elif content_type == "turtletv":
            self.video_widget = TurtleTVWidget()

        if self.video_widget:
            self.stacked_widget.addWidget(self.video_widget)

        # Set current widget
        self.stacked_widget.setCurrentWidget(self.video_widget if self.video_widget else self.featured_image_label)

        self.setStyleSheet("""
            QLabel { background-color: transparent; }
        """)

        logger.debug(f"FeaturedContent initialized with content_type: {content_type}")

        self.update_translations()

    def update_translations(self):
        self.title.setText(self.tr("Featured Content"))
        if isinstance(self.video_widget, TurtleTVWidget):
            self.title.setText(self.tr("Turtle TV"))

    def update_description(self, index):
        if isinstance(self.video_widget, TurtleTVWidget):
            pass
        logger.debug(f"Updated description for video index: {index}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        background_color = QColor(26, 29, 36, 180)
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        super().paintEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
    
    def showEvent(self, event):
        super().showEvent(event)

    def sizeHint(self):
        return QSize(640, 480)  # Suggested size