from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QStackedWidget
from PySide6.QtGui import QPixmap, QFont, QPalette, QBrush, QColor, QPainter
from PySide6.QtCore import Qt, QSize

from pathlib import Path
from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.yt_video import YouTubeVideoWidget

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
DATA = HERE / "data"
IMAGES = ASSETS / "images"

class FeaturedContent(QFrame):
    def __init__(self, content_type="image", video_id=None, featured_text=None, featured_image=None, attribution=None):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = GradientLabel("Featured Content", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Stacked Widget to switch between image and video
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Featured Image
        featured_image_label = QLabel()
        if featured_image:
            pixmap = QPixmap(featured_image)
        else:
            pixmap = QPixmap(IMAGES / "feature_image.png")
        featured_image_label.setPixmap(pixmap.scaled(QSize(630, 353), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        featured_image_label.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(featured_image_label)

        # YouTube Video
        if video_id:
            youtube_widget = YouTubeVideoWidget(video_id)
            self.stacked_widget.addWidget(youtube_widget)

        # Set the current widget based on content_type
        if content_type == "video" and video_id:
            self.stacked_widget.setCurrentWidget(youtube_widget)
        else:
            self.stacked_widget.setCurrentWidget(featured_image_label)
        
        # Featured Text
        if featured_text is not None:
            featured_text_label = QLabel(featured_text)
            featured_text_label.setWordWrap(True)
            featured_text_label.setAlignment(Qt.AlignCenter)
            featured_text_label.setFont(QFont("Arial", 11))
            featured_text_label.setStyleSheet("color: #CCCCCC;")
            layout.addWidget(featured_text_label)
        
        # Attribution Text
        if attribution is not None:
            attribution_label = QLabel(attribution)
            attribution_label.setAlignment(Qt.AlignCenter)
            attribution_label.setFont(QFont("Arial", 8))
            attribution_label.setStyleSheet("color: #FF539C;")
            layout.addWidget(attribution_label)

        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)

        # Add stretch to push content to the top
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        background_color = QColor(26, 29, 36, 180)
        
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        super().paintEvent(event)