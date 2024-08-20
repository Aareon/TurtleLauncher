from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import Qt
from pathlib import Path

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"

class StopDownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stop Download")
        self.setFixedSize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(str((FONTS / "alagard_by_pix3m.ttf").absolute()))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"  # Fallback font

        # Warning message
        warning_label = QLabel("Are you sure you want to stop the download?")
        warning_label.setFont(QFont(font_family, 14))
        warning_label.setStyleSheet("color: #FFD700;")  # Gold color
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        # Additional info
        info_label = QLabel("The download progress will be lost.")
        info_label.setFont(QFont(font_family, 12))
        info_label.setStyleSheet("color: #FF69B4;")  # Pink color
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        yes_button = QPushButton("Yes, Stop")
        no_button = QPushButton("No, Continue")

        for button in (yes_button, no_button):
            button.setFont(QFont(font_family, 12))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4B0082;
                    color: #FFD700;
                    border: 2px solid #FFD700;
                    border-radius: 10px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #8A2BE2;
                }
                QPushButton:pressed {
                    background-color: #9400D3;
                }
            """)
            button_layout.addWidget(button)

        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)

        layout.addLayout(button_layout)

        # Set dialog background
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1D24;
                border: 2px solid #FFD700;
                border-radius: 15px;
            }
        """)

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus()  # Ensure the dialog has focus when shown