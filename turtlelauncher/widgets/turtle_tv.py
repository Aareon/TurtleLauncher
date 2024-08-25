# turtle_tv.py

import json
from PySide6.QtWidgets import QVBoxLayout, QFrame, QSizePolicy, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl, Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor

from turtlelauncher.utils.config import DATA

class CustomWebEngineView(QWebEngineView):
    def createWindow(self, _):
        return None

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

        self.web_view = CustomWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.ShowScrollBars, False)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        
        self.web_view.page().fullScreenRequested.connect(self.handle_fullscreen_request)
        
        self.layout.addWidget(self.web_view)

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

        self.load_current_video()

    @staticmethod
    def load_video_data():
        videos = []
        try:
            with open(DATA / "turtletv.json") as file:
                videos = json.load(file)["videos"]
        except Exception as e:
            print(f"Failed to load TurtleTV data: {e}")
        return videos

    def load_current_video(self):
        if not self.videos:
            self.show_error("No videos available")
            return
        current_video = self.videos[self.current_index]
        self.web_view.loadFinished.connect(self.handle_load_finished)
        self.web_view.setUrl(QUrl(current_video["url"]))
        self.video_changed.emit(self.current_index)

    def handle_load_finished(self, ok):
        if ok:
            self.error_label.hide()
            self.web_view.show()
            self.inject_custom_css()
            self.adjust_video_size()
        else:
            print(f"Failed to load video: {self.web_view.url()}")
            self.show_error("Failed to load video. Please try again later.")
    
    def handle_fullscreen_request(self, request):
        if request.toggleOn():
            self.web_view.setParent(None)
            self.web_view.showFullScreen()
        else:
            self.layout.addWidget(self.web_view)
            self.web_view.showNormal()
        request.accept()

    def show_error(self, message):
        self.web_view.hide()
        self.error_label.setText(message)
        self.error_label.show()

    def next_video(self):
        self.current_index = (self.current_index + 1) % len(self.videos)
        self.load_current_video()

    def previous_video(self):
        self.current_index = (self.current_index - 1) % len(self.videos)
        self.load_current_video()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        background_color = QColor(26, 29, 36, 180)
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        super().paintEvent(event)

    def inject_custom_css(self):
        css = """
            body { background-color: transparent !important; margin: 0; padding: 0; overflow: hidden; }
        """
        js = f"var style = document.createElement('style'); style.textContent = `{css}`; document.head.appendChild(style);"
        self.web_view.page().runJavaScript(js)

    def adjust_video_size(self, available_width=None, available_height=None):
        if available_width is None:
            available_width = self.width()
        if available_height is None:
            available_height = self.height()

        js = f"""
        var iframe = document.querySelector('iframe');
        if (iframe) {{
            var aspectRatio = 16 / 9;
            var availableWidth = {available_width};
            var availableHeight = {available_height};
            var controlsHeight = 40;
            
            var videoWidth = availableWidth;
            var videoHeight = (videoWidth / aspectRatio);
            
            if (videoHeight + controlsHeight > availableHeight) {{
                videoHeight = availableHeight - controlsHeight;
                videoWidth = videoHeight * aspectRatio;
            }}
            
            iframe.style.width = videoWidth + 'px';
            iframe.style.height = videoHeight + 'px';
            iframe.style.position = 'absolute';
            iframe.style.left = ((availableWidth - videoWidth) / 2) + 'px';
            iframe.style.top = '0px';
        }}
        """
        self.web_view.page().runJavaScript(js)