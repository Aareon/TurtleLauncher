# turtlelauncher/widgets/turtle_tv.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QColor
from loguru import logger
from turtlelauncher.widgets.gradient_label import GradientLabel
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
        self.layout.setContentsMargins(0, 0, 0, 0)  # Keep margins at 0
        self.layout.setSpacing(0)  # Set spacing to 0 to remove extra space

        self.video_player = VideoWidget()
        self.video_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.video_player, alignment=Qt.AlignTop)

        # Optionally remove the stretch if you want the title layout to be closer
        #self.layout.addStretch()  # Comment this out to remove the extra space

        self.error_label = QLabel(self)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("""
            background-color: rgba(26, 29, 36, 180);
            color: #FF539C;
            font-size: 18px;
            padding: 20px;
            border-radius: 8px;
        """)
        self.error_label.hide()

        # Set error label size policy to cover the video player
        self.error_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.error_label.setGeometry(self.video_player.geometry())

        self.video_player.video_loaded.connect(self.on_video_loaded)
        self.video_player.error_occurred.connect(self.show_error)

        # Create the container for the title and buttons
        self.title_container = QWidget(self)
        self.title_layout = QHBoxLayout(self.title_container)
        self.title_layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.title_layout.setSpacing(5)  # Reduce spacing between buttons and title label

        self.title_prev_button = self.create_nav_button("◀", self.previous_video)
        self.title_layout.addWidget(self.title_prev_button)

        self.title_label = GradientLabel("", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #FFD700;
            font-size: 18px;
            background-color: rgba(0, 0, 0, 150);
            padding: 0px;
            border-radius: 5px;
        """)
        self.title_label.setFont(QFont("Fontin Sans CR", 18))
        self.title_layout.addWidget(self.title_label)

        self.title_next_button = self.create_nav_button("▶", self.next_video)
        self.title_layout.addWidget(self.title_next_button)

        # Ensure title container doesn't take extra space
        self.title_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout.addWidget(self.title_container, alignment=Qt.AlignBottom)

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
        self.title_label.setText(current_video.get("title", "Turtle TV"))
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
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 14, 78, 150);
                color: #FFD700;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(106, 26, 110, 200);
            }
        """)
        button.setFixedSize(QSize(40, 40))
        return button

    #def resizeEvent(self, event):
        #super().resizeEvent(event)
        #self.adjust_layout()

    #def adjust_layout(self):
        #video_rect = self.video_player.geometry()

        # Adjust error label to cover the video player
        #self.error_label.setGeometry(video_rect)

    def sizeHint(self):
        return QSize(16 * 40, 9 * 40)  # 16:9 aspect ratio
