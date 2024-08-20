from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt, QPoint
from pathlib import Path

class InstallationStatusDialog(QDialog):
    def __init__(self, parent=None, status="success", message=""):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Installation Status")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

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
        title_text = "Installation Complete" if status == "success" else "Installation Status"
        title = QLabel(title_text, content_widget)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title-label")
        content_layout.addWidget(title)

        # Message
        message_label = QLabel(message, content_widget)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setObjectName("message-label")
        message_label.setWordWrap(True)
        content_layout.addWidget(message_label)

        # OK button
        self.ok_button = QPushButton("OK", content_widget)
        self.ok_button.setObjectName("ok-button")
        self.ok_button.clicked.connect(self.accept)
        content_layout.addWidget(self.ok_button)

        # Close button
        close_button = QPushButton("×", content_widget)
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.close)

        # Add close button to top-right corner
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        content_layout.insertLayout(0, button_layout)

        layout.addWidget(content_widget)

        self.setStyleSheet(f"""
            #content-widget {{
                background-color: rgba(44, 47, 51, 230);
                border: 2px solid {self.get_status_color(status)};
                border-radius: 10px;
            }}
            QLabel {{
                color: #FFFFFF;
                font-size: 14px;
            }}
            #title-label {{
                font-size: 18px;
                margin: 10px 0;
            }}
            #message-label {{
                margin: 10px 0;
            }}
            QPushButton {{
                background-color: {self.get_status_color(status)};
                color: white;
                border: none;
                padding: 10px;
                margin: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.get_hover_color(status)};
            }}
            #close-button {{
                background-color: transparent;
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin: 5px;
                padding: 0;
            }}
            #close-button:hover {{
                color: #FF5555;
            }}
        """)

    def get_status_color(self, status):
        return {
            "success": "#4CAF50",
            "warning": "#FFA500",
            "error": "#F44336"
        }.get(status, "#7289DA")

    def get_hover_color(self, status):
        return {
            "success": "#45a049",
            "warning": "#FF8C00",
            "error": "#D32F2F"
        }.get(status, "#5B6EAE")

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