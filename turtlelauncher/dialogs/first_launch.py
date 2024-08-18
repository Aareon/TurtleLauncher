from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor, QMouseEvent
from PySide6.QtCore import Qt, QRect, QEvent, QPoint
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
IMAGES = ASSETS / "images"

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))  # Semi-transparent black

class FirstLaunchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        logger.debug("Initializing FirstLaunchDialog")
        self.setWindowTitle("Turtle WoW Launcher Setup")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # For dragging
        self.dragging = False
        self.drag_position = QPoint()

        # Create overlay
        self.overlay = OverlayWidget(self.parent())
        self.overlay.resize(self.parent().size())

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Content widget
        content_widget = QWidget(self)
        content_widget.setObjectName("content-widget")
        content_layout = QVBoxLayout(content_widget)

        # Logo
        logo = QLabel(content_widget)
        logo_path = IMAGES / "turtle_wow_icon.png"
        logger.debug(f"Loading logo from: {logo_path}")
        if logo_path.exists():
            logo_pixmap = QPixmap(str(logo_path)).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(logo_pixmap)
        else:
            logger.error(f"Logo file not found: {logo_path}")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo)

        # Welcome text
        welcome_label = QLabel("Welcome to Turtle WoW Launcher!", content_widget)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setObjectName("welcome-label")
        content_layout.addWidget(welcome_label)

        info_label = QLabel("Choose how you want to set up the game:", content_widget)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(info_label)

        # Buttons
        select_button = QPushButton("Select existing installation", content_widget)
        select_button.setObjectName("select-button")
        select_button.clicked.connect(self.accept)
        content_layout.addWidget(select_button)

        download_button = QPushButton("Download game", content_widget)
        download_button.setObjectName("download-button")
        download_button.clicked.connect(self.reject)
        content_layout.addWidget(download_button)

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
            #welcome-label {
                font-size: 18px;
                font-weight: bold;
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
        """)

        logger.debug("FirstLaunchDialog initialized")

    def showEvent(self, event):
        super().showEvent(event)
        logger.debug("FirstLaunchDialog showEvent triggered")
        self.overlay.show()
        self.adjustSize()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = self.parent().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def exec(self):
        logger.debug("FirstLaunchDialog exec called")
        result = super().exec()
        self.overlay.hide()
        logger.debug(f"FirstLaunchDialog exec finished with result: {result}")
        return result

    def event(self, event):
        if event.type() == QEvent.Type.WindowDeactivate:
            logger.debug("Dialog deactivated, bringing it to front")
            self.raise_()
            self.activateWindow()
            return True
        return super().event(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()