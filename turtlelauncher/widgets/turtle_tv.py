import json
from bs4 import BeautifulSoup
import cloudscraper
from loguru import logger
from PySide6.QtWidgets import QVBoxLayout, QFrame, QLabel, QWidget, QPushButton, QStackedLayout
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtMultimedia import QMediaPlayer

from turtlelauncher.utils.globals import DATA
from turtlelauncher.widgets.video_player import OpenCVVideoPlayer

class TurtleTVWidget(QFrame):
    video_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self.videos = self.load_video_data()
        self.current_index = 0
        self.next_video_url = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Use OpenCVVideoPlayer
        self.video_player = OpenCVVideoPlayer()
        self.layout.addWidget(self.video_player)

        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("""
            background-color: rgba(26, 29, 36, 180);
            color: #FF539C;
            font-size: 18px;
            padding: 20px;
            border-radius: 8px;
        """)
        self.error_label.hide()
        self.layout.addWidget(self.error_label)

        # Connect navigation buttons
        self.video_player.connect_navigation_buttons(self.previous_video, self.next_video)

        self.load_current_video()

    def handle_media_error(self, error, error_string):
        logger.error(f"Media player error: {error} - {error_string}")
        self.show_error(f"Video playback error: {error_string}")
    
    def handle_media_status_change(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            logger.debug("Media loaded successfully")
            self.preload_next_video()

    @staticmethod
    def load_video_data():
        videos = []
        try:
            with open(DATA / "turtletv.json") as file:
                videos = json.load(file)["videos"]
        except Exception as e:
            logger.error(f"Failed to load TurtleTV data: {e}")
        return videos

    def load_current_video(self):
        if not self.videos:
            self.show_error("No videos available")
            return
        current_video = self.videos[self.current_index]

        video_url = self.extract_webm_url(current_video["url"])
        if video_url:
            self.video_player.set_media(video_url)
            self.video_player.play()
            self.video_changed.emit(self.current_index)
            logger.debug(f"Playing video: {video_url}")
        else:
            self.show_error("Failed to load video. Please try again later.")
        
    def preload_next_video(self):
        next_index = (self.current_index + 1) % len(self.videos)
        next_video = self.videos[next_index]
        self.next_video_url = self.extract_webm_url(next_video["url"])
        logger.debug(f"Preloaded next video URL: {self.next_video_url}")

    def extract_webm_url(self, url):
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            video_source = soup.find('source', {'type': 'video/webm'})
            
            if video_source and video_source['src']:
                webm_url = video_source['src']
                logger.debug(f"Extracted WEBM URL: {webm_url}")
                return webm_url
            else:
                logger.error("WEBM URL not found in the HTML.")
                return None
            
        except cloudscraper.exceptions.CloudflareChallengeError as e:
            logger.error(f"Cloudflare challenge encountered: {e}")
            return None
        except Exception as e:
            logger.error(f"An error occurred while requesting {url}: {e}")
            return None

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        logger.error(f"Error shown: {message}")

    def next_video(self):
        self.video_player.stop()
        QTimer.singleShot(100, self._load_next_video)

    def previous_video(self):
        self.video_player.stop()
        self.current_index = (self.current_index - 1) % len(self.videos)
        QTimer.singleShot(100, self.load_current_video)
    
    def _load_next_video(self):
        self.current_index = (self.current_index + 1) % len(self.videos)
        if self.next_video_url:
            self.video_player.set_media(self.next_video_url)
            self.video_player.play()
            self.video_changed.emit(self.current_index)
            logger.debug(f"Playing next video: {self.next_video_url}")
            self.next_video_url = None
        else:
            self.load_current_video()

    
    def create_nav_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 14, 78, 150);
                color: #FFD700;
                border: none;
                font-size: 24px;
                font-weight: bold;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(106, 26, 110, 200);
            }
        """)
        return button

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_video_size()

    def adjust_video_size(self):
        self.video_container.setGeometry(self.rect())
        self.video_player.setGeometry(self.rect())

        # Adjust the navigation buttons
        button_size = QSize(40, 100)
        self.prev_button.setFixedSize(button_size)
        self.next_button.setFixedSize(button_size)
        self.prev_button.move(0, (self.height() - button_size.height()) // 2)
        self.next_button.move(self.width() - button_size.width(), (self.height() - button_size.height()) // 2)

    def sizeHint(self):
        return QSize(640, 360)  # 16:9 aspect ratio