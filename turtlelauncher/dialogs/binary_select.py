from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, 
                               QListWidget, QListWidgetItem, QHBoxLayout)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QPoint, Signal
from pathlib import Path
from loguru import logger

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"
DATA = HERE / "data"
IMAGES = ASSETS / "images"


class BinarySelectionDialog(QDialog):
    binary_selected = Signal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.config = config
       
        self.setWindowTitle("Select Turtle WoW Binary")
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
        title = QLabel("Select Turtle WoW Binary", content_widget)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title-label")
        content_layout.addWidget(title)

        # Binary list
        self.binary_list = QListWidget(content_widget)
        self.binary_list.setObjectName("binary-list")
        content_layout.addWidget(self.binary_list)

        game_install_dir = self.config.game_install_dir
        # Populate binary list with available binaries in game install directory
        available_binaries = [f for f in Path(game_install_dir).iterdir() if f.is_file() and f.suffix == ".exe"]

        # Determine recommended binary based on available binaries
        binary_stems = [b.stem for b in available_binaries]
        recommended_binary = None
        if len(available_binaries) == 1:
            recommended_binary = available_binaries[0]
        elif "WoW_tweaked" in binary_stems:
            recommended_binary = Path(game_install_dir) / "WoW_tweaked.exe"
        elif "WoWFoV" in binary_stems:
            recommended_binary = Path(game_install_dir) / "WoWFoV.exe"

        for binary in available_binaries:
            if binary.stem == "WoW_tweaked":
                description = "Tweaked WoW Client"
                icon_path = IMAGES / "wow_icon.png"
            elif binary.stem == "WoWFoV":
                description = "Field of View Fixes"
                icon_path = IMAGES / "wow_icon.png"
            elif binary.stem == "WoW":
                description = "Original WoW Client"
                icon_path = IMAGES / "wow_icon.png"
            else:
                description = ""
                icon_path = IMAGES / "turtle_wow_icon.png"
            
            if binary == recommended_binary:
                description += " (Recommended)"
                icon_path = IMAGES / "star.png"
            
            item = QListWidgetItem(QIcon(str(icon_path)), f"{binary.stem}\n{description}")
            item.setData(Qt.UserRole, str(binary))
            self.binary_list.addItem(item)

        # Select button
        self.select_button = QPushButton("Select", content_widget)
        self.select_button.setObjectName("select-button")
        self.select_button.clicked.connect(self.select_binary)
        content_layout.addWidget(self.select_button)

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
            #binary-scroll-area {
                border: none;
                background-color: rgba(26, 29, 36, 180);
                border-radius: 15px;
            }
            #binary-list {
                background-color: transparent;
                color: white;
                border: none;
            }
            #binary-list::item {
                padding: 5px;
            }
            #binary-list::item:selected {
                background-color: #7289DA;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(42, 45, 52, 120);
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #8e44ad;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def select_binary(self):
        selected_items = self.binary_list.selectedItems()
        if selected_items:
            selected_binary = selected_items[0].data(Qt.UserRole)
            logger.debug(f"Selected binary: {selected_binary}")
            self.binary_selected.emit(selected_binary)
            self.accept()

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