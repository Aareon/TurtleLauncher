from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QPushButton, QStyleOption, QStyle
from PySide6.QtGui import QPixmap, QFont, QPainter, QFontDatabase, QColor, QLinearGradient
from PySide6.QtCore import Qt, QSize, QRect
from pathlib import Path
from turtlelauncher.widgets.gradient_label import GradientLabel

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"
DATA = HERE / "data"
IMAGES = ASSETS / "images"

class CustomButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(120, 40)
        self.setText(text)
        self.setFont(QFont("Alagard", 12))
        self.setStyleSheet("""
            QPushButton {
                border: none;
                color: #ffd700;
                text-align: center;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(IMAGES / "PurpleButton.png")
        painter.drawPixmap(self.rect(), pixmap)
        super().paintEvent(event)

class GradientProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4a4a4a;
                border-radius: 5px;
                background-color: #2b2b2b;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the background
        bgColor = self.palette().color(self.backgroundRole())
        painter.fillRect(self.rect(), bgColor)
        
        # Calculate the progress width
        progress = self.value() - self.minimum()
        total = self.maximum() - self.minimum()
        progressWidth = progress * self.width() / total
        
        # Create and set up the gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#7700b3"))  # Start color
        gradient.setColorAt(1, QColor("#ff69b4"))  # End color
        
        # Draw the progress bar
        progressRect = QRect(0, 0, int(progressWidth), self.height())
        painter.fillRect(progressRect, gradient)

class LauncherWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 20, 0, 0)
        main_layout.setSpacing(10)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 0, 20, 20)
        content_layout.setSpacing(10)

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(str((FONTS / "alagard_by_pix3m.ttf").absolute()))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"  # Fallback font

        # Progress bar
        self.progress_label = GradientLabel("Downloading...", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        self.progress_label.setFont(QFont(font_family, 14))
        self.progress_label.setStyleSheet("color: #ffd700;")
        content_layout.addWidget(self.progress_label)

        self.progress_bar = GradientProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(80)
        self.progress_bar.setFixedHeight(20)
        content_layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.settings_button = CustomButton("Settings")
        self.play_button = CustomButton("PLAY")

        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()
        button_layout.addWidget(self.play_button)

        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()

        # Set semi-transparent background
        self.setStyleSheet("""
            LauncherWidget {
                background-color: rgba(26, 29, 36, 180);
            }
        """)

        # Set a maximum height for the LauncherWidget to limit vertical space usage
        self.setMaximumHeight(180)  # Adjust this value as needed

    def paintEvent(self, event):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        painter.setOpacity(1)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
        super().paintEvent(event)