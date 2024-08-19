from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPoint
from pathlib import Path
from loguru import logger

class InstallationDirectoryDialog(QDialog):
    def __init__(self, parent=None, is_existing_install=False):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.is_existing_install = is_existing_install
        self.setWindowTitle("Choose Installation Directory")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        self.dragging = False
        self.drag_position = QPoint()
        self.selected_directory = None

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

        # Instructions
        instructions_text = "Select where Turtle WoW is installed:" if is_existing_install else "Choose where you want to install Turtle WoW:"
        instructions = QLabel(instructions_text, content_widget)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setObjectName("instructions-label")
        content_layout.addWidget(instructions)

        # Selected directory label
        self.selected_dir_label = QLabel("No directory selected", content_widget)
        self.selected_dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_dir_label.setObjectName("selected-dir-label")
        self.selected_dir_label.setWordWrap(True)
        content_layout.addWidget(self.selected_dir_label)

        # Select directory button
        select_button = QPushButton("Select Directory", content_widget)
        select_button.setObjectName("select-button")
        select_button.clicked.connect(self.select_directory)
        content_layout.addWidget(select_button)

        # Confirm button
        self.confirm_button = QPushButton("Confirm", content_widget)
        self.confirm_button.setObjectName("confirm-button")
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setEnabled(False)
        content_layout.addWidget(self.confirm_button)

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
            #instructions-label {
                font-size: 16px;
                margin: 10px 0;
            }
            #selected-dir-label {
                font-size: 12px;
                color: #BBBBBB;
                margin: 5px 0;
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
            QPushButton:disabled {
                background-color: #4A5162;
            }
        """)

    def select_directory(self):
        dialog_title = "Select Existing Turtle WoW Directory" if self.is_existing_install else "Select Installation Directory"
        directory = QFileDialog.getExistingDirectory(self, dialog_title)
        if directory:
            self.selected_directory = directory
            self.selected_dir_label.setText(f"Selected: {directory}")
            self.confirm_button.setEnabled(True)
            logger.debug(f"Selected {'existing' if self.is_existing_install else 'installation'} directory: {directory}")

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