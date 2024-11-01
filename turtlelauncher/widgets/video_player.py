# turtlelauncher/widgets/video_player.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Signal, QSize, QUrl
from PySide6.QtGui import QColor
from loguru import logger

class VideoWidget(QWidget):
    video_loaded = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.web_view = QWebEngineView(self)
        self.web_view.setAutoFillBackground(False)

        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set page and background color to transparent
        page = self.web_view.page()
        page.setBackgroundColor(QColor(0, 0, 0, 0))
        
        layout.addWidget(self.web_view, stretch=1)
        self.setLayout(layout)

    def load_video(self, video_url):
        html_content = self.create_iframe_html(video_url)
        self.web_view.setHtml(html_content, baseUrl=QUrl("https://turtle-wow.org/"))
        self.web_view.loadFinished.connect(self.on_load_finished)

    def create_iframe_html(self, video_url):
        return f"""
        <!DOCTYPE html>
        <html style="height: 100%; margin: 0; padding: 0; overflow: hidden;">
        <head>
            <style>
                body, html {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                iframe {{
                    display: block;
                    width: 100%;
                    height: 100%;
                    border: none;
                    position: absolute;
                    top: 0;
                    left: 0;
                }}
            </style>
        </head>
        <body>
            <iframe src="{video_url}" allowfullscreen style="position: relative;"></iframe>
        </body>
        </html>
        """

    def on_load_finished(self, success):
        if success:
            logger.debug("Video iframe loaded successfully")
            self.video_loaded.emit()
        else:
            logger.error("Failed to load video iframe")
            self.error_occurred.emit(self.tr("Failed to load video"))

    def sizeHint(self):
        return QSize(1280, 1024)

    def update_size(self):
        self.resizeEvent(None)