from datetime import datetime
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QPushButton)
from PySide6.QtGui import QPixmap, QFont, QCursor
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from pathlib import Path
import logging

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TweetWidget(QFrame):
    image_clicked = Signal(QPixmap)

    def __init__(self, tweet_data):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        
        self.setStyleSheet("""
            TweetWidget {
                background-color: rgba(40, 44, 52, 180);
                border-radius: 10px;
                margin: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header: Username and timestamp
        header_layout = QHBoxLayout()
        
        username_label = QLabel(f"@{tweet_data['username']}")
        username_label.setFont(QFont("Fontin Sans", 10, QFont.Bold))
        username_label.setStyleSheet("color: #ffd700; background: transparent;")
        header_layout.addWidget(username_label)
        
        timestamp = datetime.strptime(tweet_data['timestamp'], "%Y-%m-%d %H:%M:%S")
        timestamp_label = QLabel(timestamp.strftime("%b %d, %Y at %I:%M %p"))
        timestamp_label.setFont(QFont("Fontin Sans", 8))
        timestamp_label.setStyleSheet("color: #b0b0b0; background: transparent;")
        timestamp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(timestamp_label)
        
        layout.addLayout(header_layout)

        content_label = QLabel(tweet_data['content'])
        content_label.setWordWrap(True)
        content_label.setFont(QFont("Fontin Sans", 9))
        content_label.setStyleSheet("color: #ffffff; background: transparent;")
        layout.addWidget(content_label)

        if tweet_data['links']:
            links_label = QLabel(" ".join(f'<a href="{link}" style="color: #ff69b4;">{link}</a>' for link in tweet_data['links']))
            links_label.setOpenExternalLinks(True)
            links_label.setFont(QFont("Fontin Sans", 8))
            links_label.setStyleSheet("background: transparent;")
            links_label.setWordWrap(True)  # Enable word wrap for links
            layout.addWidget(links_label)

        if tweet_data['image_url']:
            self.image_label = QPushButton()
            self.image_label.setFixedSize(QSize(300, 168))
            self.image_label.setCursor(QCursor(Qt.PointingHandCursor))
            self.image_label.clicked.connect(self.on_image_clicked)
            self.image_label.setStyleSheet("""
                QPushButton {
                    border-radius: 5px;
                    padding: 0px;
                }
                QPushButton:hover {
                }
            """)
            
            self.nam = QNetworkAccessManager()
            self.nam.finished.connect(self.set_image)
            self.nam.get(QNetworkRequest(tweet_data['image_url']))
            
            layout.addWidget(self.image_label)

    def set_image(self, reply):
        pixmap = QPixmap()
        pixmap.loadFromData(reply.readAll())
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setIcon(scaled_pixmap)
        self.image_label.setIconSize(self.image_label.size())
        self.pixmap = pixmap

    def on_image_clicked(self):
        self.image_clicked.emit(self.pixmap)
