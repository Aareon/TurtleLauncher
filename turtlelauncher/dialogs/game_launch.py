from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QProgressBar
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPoint, Signal
from pathlib import Path

class GameLaunchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Game Launch Status")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(False)  # Set to non-modal so it doesn't block the main window

        self.dragging = False
        self.drag_position = QPoint()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        content_widget = QWidget(self)
        content_widget.setObjectName("content-widget")
        content_layout = QVBoxLayout(content_widget)

        # Logo
        logo = QLabel(content_widget)
        logo_path = Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png"
        if logo_path.exists():
            logo_pixmap = QPixmap(str(logo_path)).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo)

        # Title
        title = QLabel("Game Running", content_widget)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title-label")
        content_layout.addWidget(title)

        # Progress Bar
        self.progress_bar = QProgressBar(content_widget)
        self.progress_bar.setRange(0, 0)  # This makes the progress bar indeterminate
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName("progress-bar")
        content_layout.addWidget(self.progress_bar)

        # Status Message
        self.status_label = QLabel("Game is running...", content_widget)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("status-label")
        self.status_label.setWordWrap(True)
        content_layout.addWidget(self.status_label)

        layout.addWidget(content_widget)

        self.setStyleSheet("""
            #content-widget {
                background-color: rgba(44, 47, 51, 230);
                border: 2px solid #7289DA;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            #title-label {
                font-size: 18px;
                margin: 10px 0;
            }
            #status-label {
                margin: 10px 0;
            }
            #progress-bar {
                background-color: #2C2F33;
                border: 1px solid #7289DA;
                border-radius: 5px;
                height: 20px;
            }
            #progress-bar::chunk {
                background-color: #7289DA;
                border-radius: 5px;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()