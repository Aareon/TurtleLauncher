from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QStackedWidget
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QFontDatabase
from PySide6.QtCore import Qt, QSize

from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.yt_video import YouTubeVideoWidget
from turtlelauncher.widgets.turtle_tv import TurtleTVWidget
from turtlelauncher.utils.config import FONTS, IMAGES


class FeaturedContent(QFrame):
    def __init__(self, content_type="image", video_data=None, featured_text=None, featured_image=None, attribution=None):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        font_filename = "FontinSans_Cyrillic_R_46b.ttf"
        font_id = QFontDatabase.addApplicationFont(str((FONTS / font_filename).absolute()))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"

        # Title
        title = GradientLabel("Featured Content", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(font_family, 16, QFont.Bold))
        self.layout.addWidget(title)
        
        # Stacked Widget to switch between image and video
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Featured Image
        self.featured_image_label = QLabel()
        if featured_image:
            pixmap = QPixmap(featured_image)
        else:
            pixmap = QPixmap(IMAGES / "feature_image.png")
        self.featured_image_label.setPixmap(pixmap.scaled(QSize(630, 353), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.featured_image_label.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(self.featured_image_label)

        # Video Widget
        self.video_widget = None
        if content_type in ["youtube", "turtletv"]:
            if content_type == "youtube" and video_data:
                self.video_widget = YouTubeVideoWidget(video_data)
            elif content_type == "turtletv":
                self.video_widget = TurtleTVWidget()
            self.stacked_widget.addWidget(self.video_widget)

        # Set the current widget based on content_type
        if content_type in ["youtube", "turtletv"] and video_data:
            self.stacked_widget.setCurrentWidget(self.video_widget)
        else:
            self.stacked_widget.setCurrentWidget(self.featured_image_label)
        
        # Featured Text
        self.featured_text_label = None
        if featured_text is not None:
            self.featured_text_label = QLabel(featured_text)
            self.featured_text_label.setWordWrap(True)
            self.featured_text_label.setAlignment(Qt.AlignCenter)
            self.featured_text_label.setFont(QFont("Arial", 11))
            self.featured_text_label.setStyleSheet("color: #CCCCCC;")
            self.layout.addWidget(self.featured_text_label)
        
        # Attribution Text
        self.attribution_label = None
        if attribution is not None:
            self.attribution_label = QLabel(attribution)
            self.attribution_label.setAlignment(Qt.AlignCenter)
            self.attribution_label.setFont(QFont("Arial", 8))
            self.attribution_label.setStyleSheet("color: #FF539C;")
            self.layout.addWidget(self.attribution_label)

        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)

        # Add stretch to push content to the top
        self.layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        background_color = QColor(26, 29, 36, 180)
        
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        super().paintEvent(event)

    def set_fullscreen(self, is_fullscreen):
        if is_fullscreen and self.video_widget:
            # Remove other widgets
            self.layout.removeWidget(self.featured_text_label)
            self.layout.removeWidget(self.attribution_label)
            if self.featured_text_label:
                self.featured_text_label.hide()
            if self.attribution_label:
                self.attribution_label.hide()
            
            # Expand video to fill the space
            self.video_widget.setFixedHeight(self.height() - 60)  # Adjust for padding
        else:
            # Restore original layout
            if self.featured_text_label:
                self.layout.addWidget(self.featured_text_label)
                self.featured_text_label.show()
            if self.attribution_label:
                self.layout.addWidget(self.attribution_label)
                self.attribution_label.show()
            
            # Reset video size
            if self.video_widget:
                self.video_widget.setFixedHeight(353)  # Original height

        # Update layout
        self.layout.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update video size when window is resized
        if self.video_widget and self.window().isFullScreen():
            self.video_widget.setFixedHeight(self.height() - 60)