from PySide6.QtWidgets import QPushButton, QListWidget, QListWidgetItem
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal
from pathlib import Path
from loguru import logger
from PIL.ImageQt import ImageQt

from turtlelauncher.dialogs.base import BaseDialog
from turtlelauncher.utils.game_utils import get_exe_icon

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
FONTS = ASSETS / "fonts"
DATA = HERE / "data"
IMAGES = ASSETS / "images"


class BinarySelectionDialog(BaseDialog):
    binary_selected = Signal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent, title="Select Turtle WoW Binary", icon_path=str(Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png"))
        self.config = config

        self.setup_binary_list()
        self.setup_select_button()
    
    def populate_binary_list(self):
        game_install_dir = self.config.game_install_dir
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
            elif binary.stem == "WoWFoV":
                description = "Field of View Fixes"
            elif binary.stem == "WoW":
                description = "Original WoW Client"
            else:
                description = ""
            
            if binary == recommended_binary:
                description += " (Recommended)"
                icon = QIcon(str(IMAGES / "star.png"))
            else:
                # Get the icon for the binary
                try:
                    icon_image = get_exe_icon(binary)
                    qimage = ImageQt(icon_image)
                    icon = QIcon(QPixmap.fromImage(qimage))
                except Exception as e:
                    logger.warning(f"Failed to get icon for {binary}: {e}")
                    icon = QIcon(str(IMAGES / "turtle_wow_icon.png"))

            item = QListWidgetItem(icon, f"{binary.stem}\n{description}")
            item.setData(Qt.UserRole, str(binary))
            self.binary_list.addItem(item)

            # Highlight the previously selected binary
            if str(binary) == self.config.selected_binary:
                self.binary_list.setCurrentItem(item)
                logger.debug(f"Preselected binary: {binary}")

    def select_binary(self):
        selected_items = self.binary_list.selectedItems()
        if selected_items:
            selected_binary = selected_items[0].data(Qt.UserRole)
            logger.debug(f"Selected binary: {selected_binary}")
            
            # Save the selected binary path to the config
            self.config.selected_binary = selected_binary
            self.config.save()
            logger.info(f"Saved selected binary path to config: {selected_binary}")
            
            self.binary_selected.emit(selected_binary)
            self.accept()
        else:
            logger.warning("No binary selected")

    def setup_binary_list(self):
        self.binary_list = QListWidget(self.content_widget)
        self.binary_list.setObjectName("binary-list")
        self.content_layout.addWidget(self.binary_list)

        self.populate_binary_list()
    
    def setup_select_button(self):
        self.select_button = QPushButton("Select", self.content_widget)
        self.select_button.setObjectName("select-button")
        self.select_button.clicked.connect(self.select_binary)
        self.content_layout.addWidget(self.select_button)
    
    def generate_stylesheet(self, custom_styles=None):
        base_stylesheet = super().generate_stylesheet(custom_styles)
        additional_styles = """
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
        """
        return base_stylesheet + additional_styles