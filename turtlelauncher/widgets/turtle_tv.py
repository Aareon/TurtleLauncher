from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from loguru import logger
from turtlelauncher.utils.globals import DATA
from turtlelauncher.widgets.video_player import VideoWidget
import json

class TurtleTVWidget(QFrame):
    video_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self.videos = self.load_video_data()
        self.current_index = 0
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.video_player = VideoWidget()
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

        self.video_player.video_loaded.connect(self.on_video_loaded)
        self.video_player.error_occurred.connect(self.show_error)

        self.prev_button = self.create_nav_button("◀", self.previous_video)
        self.next_button = self.create_nav_button("▶", self.next_video)

        QTimer.singleShot(0, self.load_current_video)

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
        self.video_player.load_video(current_video["url"])
        self.video_changed.emit(self.current_index)
        logger.debug(f"Loading video: {current_video['url']}")

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        logger.error(f"Error shown: {message}")

    def next_video(self):
        self.current_index = (self.current_index + 1) % len(self.videos)
        self.load_current_video()

    def previous_video(self):
        self.current_index = (self.current_index - 1) % len(self.videos)
        self.load_current_video()

    def on_video_loaded(self):
        logger.debug("Video loaded successfully")

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
        self.video_player.setGeometry(self.rect())
        self.video_player.update_size()

        button_size = QSize(40, 100)
        self.prev_button.setFixedSize(button_size)
        self.next_button.setFixedSize(button_size)
        self.prev_button.move(10, (self.height() - button_size.height()) // 2)
        self.next_button.move(self.width() - button_size.width() - 10, (self.height() - button_size.height()) // 2)

    def sizeHint(self):
        return QSize(16 * 40, 9 * 40)  # 16:9 aspect ratio