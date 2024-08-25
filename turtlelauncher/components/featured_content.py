# featured_content.py

from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QStackedWidget, QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QFontDatabase
from PySide6.QtCore import Qt, QTimer, QSize

from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.yt_video import YouTubeVideoWidget
from turtlelauncher.widgets.turtle_tv import TurtleTVWidget
from turtlelauncher.utils.config import FONTS, IMAGES

class FeaturedContent(QFrame):
    def __init__(self, content_type="image", video_data=None, featured_image=None):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(600, 400)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Title
        font_filename = "FontinSans_Cyrillic_R_46b.ttf"
        font_id = QFontDatabase.addApplicationFont(str((FONTS / font_filename).absolute()))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        
        self.title = GradientLabel("Featured Content", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
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
            self.title.setText("Turtle TV")

        if self.video_widget:
            self.stacked_widget.addWidget(self.video_widget)

        # Set current widget
        self.stacked_widget.setCurrentWidget(self.video_widget if self.video_widget else self.featured_image_label)

        # Controls
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 10, 0, 0)
        controls_layout.setSpacing(10)

        self.prev_button = QPushButton("←")
        self.next_button = QPushButton("→")
        self.prev_button.setFixedSize(QSize(40, 40))
        self.next_button.setFixedSize(QSize(40, 40))

        if isinstance(self.video_widget, TurtleTVWidget):
            self.prev_button.clicked.connect(self.video_widget.previous_video)
            self.next_button.clicked.connect(self.video_widget.next_video)
            self.video_widget.video_changed.connect(self.update_description)
        
        self.title_label = GradientLabel("", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setStyleSheet("background-color: transparent;")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title_label.setMinimumWidth(200)

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.title_label, 1)
        controls_layout.addWidget(self.next_button)

        self.layout.addWidget(controls_widget)

        self.setStyleSheet("""
            QLabel { background-color: transparent; }
            QPushButton {
                background-color: #4a0e4e;
                color: #FFD700;
                border: 2px solid #FF69B4;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a1a6e;
                border-color: #FFD700;
            }
        """)

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.adjust_layout)
        
        self.update_description(self.video_widget.current_index)

    def update_description(self, index):
        if isinstance(self.video_widget, TurtleTVWidget):
            self.title_label.setText(self.video_widget.videos[index]["title"])

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
        self.resize_timer.start(200)

    def adjust_layout(self):
        if isinstance(self.video_widget, TurtleTVWidget):
            available_width = self.stacked_widget.width()
            available_height = self.stacked_widget.height()
            self.video_widget.adjust_video_size(available_width, available_height)