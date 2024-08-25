import json
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, 
                               QScrollArea, QFrame, QSizePolicy)
from PySide6.QtGui import QFont, QColor, QFontDatabase, QPixmap
from PySide6.QtCore import Qt, Signal
from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.image_overlay import ImageOverlay
from turtlelauncher.widgets.tweet import TweetWidget
from turtlelauncher.utils.config import Config


HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"


class TweetsFeed(QWidget):
    image_clicked = Signal(QPixmap)

    def __init__(self, config: Config, json_file_path):
        super().__init__()
        self.config = config
        self.setMinimumWidth(320)
        
        font_filename = "FontinSans_Cyrillic_R_46b.ttf"
        font_id = QFontDatabase.addApplicationFont(str((FONTS / font_filename).absolute()))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background-color: rgba(26, 29, 36, 180);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = GradientLabel("Latest Tweets", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(font_family, 18, QFont.Bold))
        title.setStyleSheet("padding: 15px; background: transparent;")
        title_layout.addWidget(title)

        layout.addWidget(title_container)
        
        tweets_scroll = QScrollArea()
        tweets_scroll.setWidgetResizable(True)
        tweets_scroll.setFrameShape(QFrame.NoFrame)
        tweets_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: rgba(26, 29, 36, 180);
                border-radius: 15px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(42, 45, 52, 120);
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #8e44ad;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        tweets_content = QWidget()
        tweets_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tweets_content_layout = QVBoxLayout(tweets_content)
        tweets_content_layout.setContentsMargins(10, 10, 10, 10)
        tweets_content_layout.setSpacing(15)
        tweets_content.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        with open(json_file_path, 'r', encoding='utf-8') as file:
            tweets_data = json.load(file)
        
        for tweet_data in tweets_data:
            tweet_widget = TweetWidget(tweet_data)
            tweet_widget.image_clicked.connect(self.on_image_clicked)
            tweets_content_layout.addWidget(tweet_widget)
        
        tweets_content_layout.addStretch()
        tweets_scroll.setWidget(tweets_content)
        layout.addWidget(tweets_scroll)

        self.setStyleSheet("""
            TweetsWidget {
                background-color: transparent;
            }
        """)

        self.image_overlay = None

    def on_image_clicked(self, pixmap):
        self.image_clicked.emit(pixmap)

    def on_overlay_closed(self):
        self.image_overlay = None
