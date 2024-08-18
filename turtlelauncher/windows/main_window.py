from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import  QPixmap, QPalette, QBrush
from turtlelauncher.components.tweets_feed import TweetsFeed
from turtlelauncher.components.featured_content import FeaturedContent
from turtlelauncher.widgets.launcher import LauncherWidget
from turtlelauncher.widgets.image_overlay import ImageOverlay
from turtlelauncher.components.header import HeaderWidget
from pathlib import Path

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
DATA = ASSETS / "data"
IMAGES = ASSETS / "images"

class TurtleWoWLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Turtle WoW Launcher")
        self.setMinimumSize(1200, 800)
        
        # Set the window icon
        icon = QPixmap(IMAGES / "turtle_wow_icon.png")
        self.setWindowIcon(icon)

        # Set background image
        background = QPixmap(IMAGES / "background.png")
        background_brush = QBrush(background)
        palette = self.palette()
        palette.setBrush(QPalette.Window, background_brush)
        self.setPalette(palette)

        central_widget = QWidget()
        central_widget.setAutoFillBackground(False)  # Make the central widget transparent
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_widget = HeaderWidget()
        main_layout.addWidget(header_widget)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        tweets_and_featured_layout = QHBoxLayout()
        tweets_widget = TweetsFeed(DATA / "tweets.json")
        tweets_widget.image_clicked.connect(self.show_image_overlay)
        featured_content_widget = FeaturedContent()
        
        self.image_overlay = None
        
        # Set size policies to allow widgets to expand
        tweets_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        featured_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        tweets_and_featured_layout.addWidget(tweets_widget, 1)  # Give less space to tweets
        tweets_and_featured_layout.addWidget(featured_content_widget, 2)  # Give more space to featured content
        content_layout.addLayout(tweets_and_featured_layout)

        main_layout.addWidget(content_widget, 1)  # Allow content to expand

        # Launcher Widget
        launcher_widget = LauncherWidget()
        main_layout.addWidget(launcher_widget)

        self.setCentralWidget(central_widget)

        # Set the overall style
        self.setStyleSheet("""
            QMainWindow {
                border: none;
            }
        """)
    
    def show_image_overlay(self, pixmap):
        if self.image_overlay:
            self.image_overlay.close()
        
        self.image_overlay = ImageOverlay(pixmap, self)
        self.image_overlay.closed.connect(self.on_overlay_closed)
        
        # Set the size of the overlay to match the main window
        self.image_overlay.setGeometry(self.rect())
        self.image_overlay.show()
    
    def on_overlay_closed(self):
        self.image_overlay = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize the image overlay if it exists
        if self.image_overlay:
            self.image_overlay.setGeometry(self.rect())
