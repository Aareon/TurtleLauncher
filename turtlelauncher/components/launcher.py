from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStyleOption, QStyle, QLabel
from PySide6.QtGui import QFont, QPainter, QFontDatabase, QColor
from PySide6.QtCore import Slot, Signal, QTimer
from pathlib import Path
from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.image_button import ImageButton
from turtlelauncher.widgets.gradient_progressbar import GradientProgressBar
from turtlelauncher.utils.downloader import DownloadExtractUtility
import logging

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"
DATA = HERE / "data"
IMAGES = ASSETS / "images"

class LauncherWidget(QWidget):
    download_completed = Signal()
    extraction_completed = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.download_utility = DownloadExtractUtility()
        self.download_utility.progress_updated.connect(self.update_progress)
        self.download_utility.download_completed.connect(self.on_download_completed)
        self.download_utility.extraction_completed.connect(self.on_extraction_completed)
        self.download_utility.error_occurred.connect(self.on_error)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(str((FONTS / "alagard_by_pix3m.ttf").absolute()))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"  # Fallback font

        # Progress info layout
        progress_info_layout = QHBoxLayout()
        progress_info_layout.setContentsMargins(0, 0, 0, 5)

        self.progress_label = GradientLabel("Waiting...", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        self.progress_label.setFont(QFont(font_family, 14))
        self.progress_label.setMinimumWidth(300)  # Ensure enough width for the label
        progress_info_layout.addWidget(self.progress_label)

        progress_info_layout.addStretch()

        self.speed_label = QLabel("0 MB/s")
        self.speed_label.setFont(QFont(font_family, 10))
        self.speed_label.setStyleSheet("color: #ffd700;")
        progress_info_layout.addWidget(self.speed_label)

        self.percent_label = QLabel("0%")
        self.percent_label.setFont(QFont(font_family, 10))
        self.percent_label.setStyleSheet("color: #ffd700;")
        progress_info_layout.addWidget(self.percent_label)

        main_layout.addLayout(progress_info_layout)

        self.progress_bar = GradientProgressBar()
        self.progress_bar.setAnimationSpeed(0.5)  # Set animation speed (pixels per frame)
        self.progress_bar.setAnimationFrequency(0.5)  # One cycle every 2 seconds
        self.progress_bar.setGradientWidth(300) # Set the width of the gradient to 300 pixels
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        main_layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.settings_button = ImageButton("PurpleButton.png", "Settings", "Alagard")
        self.play_button = ImageButton("PurpleButton.png", "PLAY", "Alagard")

        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()
        button_layout.addWidget(self.play_button)

        main_layout.addLayout(button_layout)

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

    @Slot(int, str)
    def update_progress(self, percent, speed):
        self.progress_label.setText(f"Downloading... {percent}%")
        self.speed_label.setText(speed)
        self.percent_label.setText(f"{percent}%")
        self.progress_bar.setValue(percent)

    @Slot()
    def on_download_completed(self):
        self.progress_label.setText("Download completed. Extracting...")
        self.speed_label.setText("")
        self.percent_label.setText("0%")
        self.progress_bar.setValue(0)
        self.download_completed.emit()

    @Slot()
    def on_extraction_completed(self):
        self.progress_label.setText("Installation completed!")
        self.speed_label.setText("")
        self.percent_label.setText("100%")
        self.progress_bar.setValue(100)
        self.extraction_completed.emit()

    @Slot(str)
    def on_error(self, error_message):
        self.progress_label.setText(f"Error: {error_message}")
        self.error_occurred.emit(error_message)

    def start_download(self, url, extract_path):
        self.progress_label.setText("Preparing download...")
        self.speed_label.setText("")
        self.percent_label.setText("0%")
        self.progress_bar.setValue(0)
        logger.debug(f"Starting download from {url} to {extract_path}")
        QTimer.singleShot(0, lambda: self.download_utility.download_and_extract(url, extract_path))