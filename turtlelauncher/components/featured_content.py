from loguru import logger
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QStackedWidget, QWidget
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QFontDatabase
from PySide6.QtCore import Qt, QSize, QTimer

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
        logger.info(f"Loaded font: {font_family}")

        # Title
        self.title = GradientLabel("Featured Content", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont(font_family, 16, QFont.Bold))
        self.layout.addWidget(self.title)
        
        # Stacked Widget to switch between image and video
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget, 1)  # Give it a stretch factor of 1

        # Featured Image
        self.featured_image_label = QLabel()
        if featured_image:
            pixmap = QPixmap(featured_image)
        else:
            pixmap = QPixmap(IMAGES / "feature_image.png")
        self.featured_image_label.setPixmap(pixmap)
        self.featured_image_label.setScaledContents(True)
        self.featured_image_label.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(self.featured_image_label)

        # Video Widget
        self.video_widget = None
        if content_type in ["youtube", "turtletv"]:
            if content_type == "youtube" and video_data:
                self.video_widget = YouTubeVideoWidget(video_data)
            elif content_type == "turtletv":
                self.video_widget = TurtleTVWidget()
                self.title.setText("Turtle TV")
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

        # Set up a timer to check for window size changes
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.adjust_layout)
        self.last_width = self.width()

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
        else:
            # Restore original layout
            if self.featured_text_label:
                self.layout.addWidget(self.featured_text_label)
                self.featured_text_label.show()
            if self.attribution_label:
                self.layout.addWidget(self.attribution_label)
                self.attribution_label.show()

        self.adjust_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Start the timer to adjust layout after resizing stops
        self.resize_timer.start(200)  # 200ms delay

    def adjust_layout(self):
        window = self.window()
        if window:
            window_width = window.width()
            window_height = window.height()
            is_maximized = window.isMaximized()

            if is_maximized:
                # Allow full width when maximized
                self.setMaximumWidth(16777215)  # QWIDGETSIZE_MAX
                max_height = window_height - 100  # Adjust as needed for other UI elements
            else:
                # Set width to 60% of window width when not maximized
                max_width = min(window_width * 0.6, 1000)  # Cap at 1000px
                self.setMaximumWidth(int(max_width))
                max_height = window_height - 150  # More space for other elements when not maximized

            # Calculate the maximum content size while maintaining aspect ratio
            content_width = self.width() - 30  # Accounting for margins
            content_height = int(content_width * 9 / 16)  # 16:9 aspect ratio

            if content_height > max_height:
                content_height = max_height
                content_width = int(content_height * 16 / 9)

            content_size = QSize(content_width, content_height)

            # Adjust content size
            if self.featured_image_label.pixmap():
                self.featured_image_label.setPixmap(self.featured_image_label.pixmap().scaled(
                    content_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
            if self.video_widget:
                self.video_widget.setFixedSize(content_size)

            # Adjust title font size
            title_font = self.title.font()
            title_font.setPointSize(max(12, min(16, int(content_width / 30))))
            self.title.setFont(title_font)

        self.update()