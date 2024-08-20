from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtGui import QFont, QFontDatabase, QPixmap
from PySide6.QtCore import Qt, QPoint, Signal
from pathlib import Path

class StopDownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Stop Download")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        self.dragging = False
        self.drag_position = QPoint()

        self.setup_ui()

    def setup_ui(self):
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
        title = QLabel("Stop Download", content_widget)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title-label")
        content_layout.addWidget(title)

        # Warning message
        warning_label = QLabel("Are you sure you want to stop the download?", content_widget)
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setWordWrap(True)
        warning_label.setObjectName("warning-label")
        content_layout.addWidget(warning_label)

        # Additional info
        info_label = QLabel("The download progress will be lost.", content_widget)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setObjectName("info-label")
        content_layout.addWidget(info_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.yes_button = QPushButton("Yes, Stop", content_widget)
        self.no_button = QPushButton("No, Continue", content_widget)

        for button in (self.yes_button, self.no_button):
            button.setObjectName("dialog-button")
            button_layout.addWidget(button)

        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)

        content_layout.addLayout(button_layout)

        # Close button
        close_button = QPushButton("×", content_widget)
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.reject)

        # Add close button to top-right corner
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(close_button)
        content_layout.insertLayout(0, top_layout)

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
            #warning-label {
                color: #FFD700;
                font-size: 16px;
                margin: 10px 0;
            }
            #info-label {
                color: #FF69B4;
                font-size: 14px;
                margin: 5px 0;
            }
            #dialog-button {
                background-color: #7289DA;
                color: white;
                border: none;
                padding: 10px;
                margin: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            #dialog-button:hover {
                background-color: #5B6EAE;
            }
            #close-button {
                background-color: transparent;
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin: 5px;
                padding: 0;
            }
            #close-button:hover {
                color: #FF5555;
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