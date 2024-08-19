from PySide6.QtWidgets import QHBoxLayout, QLabel, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from pathlib import Path
import logging
from turtlelauncher.widgets.icon_button import IconButton

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
DATA = ASSETS / "data"
IMAGES = ASSETS / "images"


class HeaderWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(0)  # Set spacing to 0 to control it manually

        # Logo on the left
        logo_label = QLabel()
        logo_path = IMAGES / "turtle_wow_logo.png"
        logo_pixmap = QPixmap(str(logo_path))
        if logo_pixmap.isNull():
            logger.error(f"Failed to load logo: {logo_path}")
        else:
            logo_label.setPixmap(logo_pixmap.scaled(200, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_label)

        # Spacer to push icons to the right
        layout.addStretch()

        # Discord icon
        discord_icon = IconButton(IMAGES / "discord.png", "https://discord.gg/turtlewow", 28)
        layout.addWidget(discord_icon)

        # Add spacer between icons (full icon width)
        layout.addSpacing(24)

        # GitHub icon
        github_icon = IconButton(IMAGES / "github-white.png", "https://github.com/turtle-wow", 24)
        layout.addWidget(github_icon)

        # Add spacer between icons (full icon width)
        layout.addSpacing(24)

        # Patreon icon
        patreon_icon = IconButton(IMAGES / "patreon-icon.png", "https://www.patreon.com/turtlewow", 24)
        layout.addWidget(patreon_icon)

        # Set semi-transparent background color
        self.setStyleSheet("""
            HeaderWidget {
                background-color: rgba(26, 29, 36, 180);  /* 85%  opacity */
            }
        """)

        self.setFixedHeight(70)  # Set a fixed height for the header

    def paintEvent(self, event):
        super().paintEvent(event)
        logger.debug(f"Header widget size: {self.size()}")
        logger.debug(f"Header widget background color: {self.palette().color(self.backgroundRole()).name()}")