from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPoint
from pathlib import Path

class GenericConfirmationDialog(QDialog):
    def __init__(self, parent=None, title="Confirmation", message="", confirm_text="OK", cancel_text="Cancel", icon_path=None, custom_styles=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(title)
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
        if icon_path:
            logo = QLabel(content_widget)
            icon_path = Path(icon_path)
            if icon_path.exists():
                logo_pixmap = QPixmap(str(icon_path)).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo.setPixmap(logo_pixmap)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(logo)

        # Title
        title_label = QLabel(title, content_widget)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title-label")
        content_layout.addWidget(title_label)

        # Message
        if isinstance(message, str):
            message_label = QLabel(message, content_widget)
            message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message_label.setObjectName("message-label")
            message_label.setWordWrap(True)
            content_layout.addWidget(message_label)
        elif isinstance(message, list):
            for idx, msg in enumerate(message):
                msg_label = QLabel(msg, content_widget)
                msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                msg_label.setObjectName(f"message-label-{idx}")
                msg_label.setWordWrap(True)
                content_layout.addWidget(msg_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton(confirm_text, content_widget)
        self.confirm_button.setObjectName("confirm-button")
        self.confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_button)

        if cancel_text:
            self.cancel_button = QPushButton(cancel_text, content_widget)
            self.cancel_button.setObjectName("cancel-button")
            self.cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(self.cancel_button)

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

        self.setStyleSheet(self.generate_stylesheet(custom_styles))

    def generate_stylesheet(self, custom_styles):
        base_stylesheet = """
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
            .message-label {
                margin: 10px 0;
            }
            QPushButton {
                background-color: #7289DA;
                color: white;
                border: none;
                padding: 10px;
                margin: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
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
        """
        
        if custom_styles:
            for selector, style in custom_styles.items():
                base_stylesheet += f"\n{selector} {{\n"
                for property, value in style.items():
                    base_stylesheet += f"    {property}: {value};\n"
                base_stylesheet += "}\n"
        
        return base_stylesheet

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