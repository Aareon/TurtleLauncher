import json

from loguru import logger
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QMovie

from turtlelauncher.utils.config import DATA


class TurtleTVWidget(QFrame):
    video_changed = Signal(int)  # Signal to emit when video changes

    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self.video_urls = self.load_video_data()
        self.current_index = 0
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Video player
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.web_view.loadStarted.connect(self.show_loading)
        self.web_view.loadFinished.connect(self.hide_loading)
        self.layout.addWidget(self.web_view)

        # Loading overlay
        self.loading_overlay = QLabel(self)
        self.loading_movie = QMovie("path/to/loading.gif")  # Replace with actual path
        self.loading_overlay.setMovie(self.loading_movie)
        self.loading_overlay.setAlignment(Qt.AlignCenter)
        self.loading_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.loading_overlay.hide()

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("←")
        self.next_button = QPushButton("→")
        self.prev_button.clicked.connect(self.previous_video)
        self.next_button.clicked.connect(self.next_video)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        self.layout.addLayout(nav_layout)

        # Video Description
        self.description = QLabel("Check out our featured video content!")
        self.description.setWordWrap(True)
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setStyleSheet("font-family: Arial; font-size: 11px; color: #CCCCCC;")
        self.layout.addWidget(self.description)

        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
        """)

        self.load_current_video()
    
    @staticmethod
    def load_video_data():
        videos = []
        try:
            with open(DATA / "turtletv.json") as file:
                videos = json.load(file)["videos"]
        except Exception:
            logger.exception("Failed to load TurtleTV data")
        finally:
            return videos

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        background_color = QColor(26, 29, 36, 180)
        
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        super().paintEvent(event)

    def load_current_video(self):
        self.web_view.setUrl(QUrl(self.video_urls[self.current_index]))
        self.video_changed.emit(self.current_index)

    def next_video(self):
        self.current_index = (self.current_index + 1) % len(self.video_urls)
        self.load_current_video()

    def previous_video(self):
        self.current_index = (self.current_index - 1) % len(self.video_urls)
        self.load_current_video()

    def show_loading(self):
        self.loading_overlay.setGeometry(self.web_view.geometry())
        self.loading_movie.start()
        self.loading_overlay.show()

    def hide_loading(self):
        QTimer.singleShot(500, self._hide_loading)  # Delay to ensure video is ready

    def _hide_loading(self):
        self.loading_movie.stop()
        self.loading_overlay.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.loading_overlay.setGeometry(self.web_view.geometry())