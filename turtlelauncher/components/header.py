from PySide6.QtWidgets import QHBoxLayout, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from pathlib import Path
from loguru import logger
from turtlelauncher.widgets.icon_button import IconButton

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
        logo_path = IMAGES / "turtle_wow_logo.png"
        logo_button = IconButton(logo_path, "https://turtle-wow.org/", 150)
        logo_button.setFixedSize(200, 50)  # Set fixed size for the logo button
        logo_button.setStyleSheet("IconButton { border: none; }")  # Remove any border
        layout.addWidget(logo_button)

        # Spacer to push icons to the right
        layout.addStretch()

        # Discord icon
        discord_icon = IconButton(IMAGES / "discord.png", "https://discord.gg/turtlewow", 28)
        layout.addWidget(discord_icon)

        # Add spacer between icons (full icon width)
        layout.addSpacing(24)

        # GitHub icon
        github_icon = IconButton(IMAGES / "github-white.png", "https://github.com/Aareon/TurtleLauncher", 24)
        layout.addWidget(github_icon)

        # Add spacer between icons (full icon width)
        layout.addSpacing(24)

        # Patreon icon
        patreon_icon = IconButton(IMAGES / "patreon-icon.png", "https://www.patreon.com/askully", 24)
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