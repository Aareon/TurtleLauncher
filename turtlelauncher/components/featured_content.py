from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import QPixmap, QFont, QPalette, QBrush, QColor, QPainter
from PySide6.QtCore import Qt, QSize

from pathlib import Path
from turtlelauncher.widgets.gradient_label import GradientLabel

HERE = Path(__file__).parent
ASSETS = HERE.parent.parent / "assets"
DATA = HERE / "data"
IMAGES = ASSETS / "images"

class FeaturedContent(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = GradientLabel("Featured Content", QColor(255, 215, 0), QColor(255, 105, 180), intensity=2.0, vertical=True)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Featured Image
        featured_image = QLabel()
        pixmap = QPixmap(IMAGES / "feature_image.png")
        featured_image.setPixmap(pixmap.scaled(QSize(630, 353), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        featured_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(featured_image)
        
        # Featured Text
        featured_text = QLabel("Under the guise of the full moons, a bloodied terror skulks Karazhan.\nBeware to not fall prey to his ravenous fangs...")
        featured_text.setWordWrap(True)
        featured_text.setAlignment(Qt.AlignCenter)
        featured_text.setFont(QFont("Arial", 11))
        featured_text.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(featured_text)
        
        # Attribution Text
        attribution = QLabel("Artwork by: John Doe")
        attribution.setAlignment(Qt.AlignCenter)
        attribution.setFont(QFont("Arial", 8))
        attribution.setStyleSheet("color: #FF539C;")
        layout.addWidget(attribution)

        # Remove the background color setting from here
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)

        # Add stretch to push content to the top
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create a semi-transparent dark color
        background_color = QColor(26, 29, 36, 180)
        
        # Draw the rounded rectangle background
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        super().paintEvent(event)