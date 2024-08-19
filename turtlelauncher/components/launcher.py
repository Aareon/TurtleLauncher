from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStyleOption, QStyle, QLabel
from PySide6.QtGui import QFont, QPainter, QFontDatabase, QColor
from PySide6.QtCore import Slot, Signal, QTimer, Qt
from pathlib import Path
from turtlelauncher.widgets.gradient_label import GradientLabel
from turtlelauncher.widgets.image_button import ImageButton
from turtlelauncher.widgets.gradient_progressbar import GradientProgressBar
from turtlelauncher.utils.downloader import DownloadExtractUtility
from loguru import logger

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
        self.download_utility.status_changed.connect(self.on_status_changed)
        self.download_utility.total_size_updated.connect(self.set_total_file_size)

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

        self.total_size_label = QLabel("Total size: 0 MB")
        self.total_size_label.setFont(QFont(font_family, 10))
        self.total_size_label.setStyleSheet("color: #ffd700;")
        progress_info_layout.addWidget(self.total_size_label)

        main_layout.addLayout(progress_info_layout)

        self.progress_bar = GradientProgressBar()
        self.progress_bar.setAnimationSpeed(0.5)
        self.progress_bar.setGradientWidth(1000)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        main_layout.addWidget(self.progress_bar)

        # Version Label
        self.version_label = QLabel()
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.version_label.setStyleSheet("color: #ffd700; font-size: 14px;")
        self.version_label.hide()  # Initially hide the version label
        main_layout.addWidget(self.version_label)

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

    @Slot(str, str)
    def update_progress(self, percent, speed):
        percent_int = int(float(percent))  # Convert percent to integer
        if self.progress_label.text().startswith("Extracting"):
            self.progress_label.setText(f"Extracting... {percent_int}%")
        else:
            self.progress_label.setText(f"Downloading... {percent_int}%")
        self.speed_label.setText(speed)
        self.progress_bar.setValue(percent_int)

    @Slot()
    def on_download_completed(self):
        self.progress_label.setText("Extracting...")
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
        self.progress_bar.stop_particle_effect()
        self.extraction_completed.emit()

    @Slot(str)
    def on_error(self, error_message):
        self.progress_label.setText(f"Error: {error_message}")
        self.progress_bar.stop_particle_effect()
        self.error_occurred.emit(error_message)
    
    @Slot(bool)
    def on_status_changed(self, is_downloading):
        if is_downloading:
            self.progress_bar.start_particle_effect()
        else:
            self.progress_bar.stop_particle_effect()

    def start_download(self, url, extract_path):
        self.progress_label.setText("Preparing download...")
        self.speed_label.setText("")
        self.total_size_label.setText("Total size: Calculating...")
        self.progress_bar.setValue(0)
        logger.debug(f"Starting download from {url} to {extract_path}")
        QTimer.singleShot(0, lambda: self.download_utility.download_and_extract(url, extract_path))

    def display_version_info(self, version):
        version_str = f"Turtle WoW Version: {version}"
        self.version_label.setText(version_str)
        self.version_label.show()
        self.hide_progress_widgets()
        logger.info(f"Displaying version info: {version_str}")

    def hide_progress_widgets(self):
        self.progress_bar.hide()
        self.progress_label.hide()
        self.speed_label.hide()
        self.percent_label.hide()

    def show_progress_widgets(self):
        self.progress_bar.show()
        self.progress_label.show()
        self.speed_label.show()
        self.percent_label.show()
    
    @Slot(str)
    def set_total_file_size(self, total_size_str):
        try:
            total_size_bytes = int(total_size_str)
            if total_size_bytes > 0:
                if total_size_bytes >= 1024 * 1024 * 1024:  # If size is 1 GB or larger
                    total_size_gb = total_size_bytes / (1024 * 1024 * 1024)
                    self.total_size_label.setText(f"Total size: {total_size_gb:.2f} GB")
                else:
                    total_size_mb = total_size_bytes / (1024 * 1024)
                    self.total_size_label.setText(f"Total size: {total_size_mb:.2f} MB")
            else:
                self.total_size_label.setText("Total size: Unknown")
        except ValueError:
            logger.error(f"Invalid total size received: {total_size_str}")
            self.total_size_label.setText("Total size: Unknown")
        except Exception as e:
            logger.error(f"Error setting total file size: {e}")
            self.total_size_label.setText("Total size: Error")