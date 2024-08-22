from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QPainter, QColor

class YouTubeVideoWidget(QFrame):
    def __init__(self, video_id):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # YouTube Video
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.web_view.setUrl(QUrl(f"https://www.youtube.com/embed/{video_id}"))
        layout.addWidget(self.web_view)

        # Video Description
        description = QLabel("Check out our featured video content!")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("font-family: Arial; font-size: 11px; color: #CCCCCC;")
        layout.addWidget(description)

        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        background_color = QColor(26, 29, 36, 180)
        
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        super().paintEvent(event)