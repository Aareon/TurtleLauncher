from PySide6.QtWidgets import QProgressBar
from PySide6.QtGui import QPainter, QLinearGradient, QColor
from PySide6.QtCore import QRect

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