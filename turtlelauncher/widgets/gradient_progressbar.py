from PySide6.QtWidgets import QProgressBar
from PySide6.QtGui import QPainter, QLinearGradient, QColor
from PySide6.QtCore import QRect, QTimer, Qt, Property

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
        
        self._offset = 0.0
        self._gradient_width = 200  # Width of one complete gradient cycle
        self._animation_speed = 2  # Pixels to move per frame
        self._animation_frequency = 1  # Number of complete cycles per second

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_offset)
        self._timer.start(16)  # Update every 16ms (approximately 60 FPS)

        self._smooth_value = 0.0

    def _update_offset(self):
        # Calculate movement based on speed and frequency
        movement = (self._animation_speed * self._animation_frequency * self._gradient_width) / 60
        self._offset = (self._offset + movement) % self._gradient_width
        
        # Smooth value update
        target_value = self.value()
        self._smooth_value += (target_value - self._smooth_value) * 0.1
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the background
        bgColor = self.palette().color(self.backgroundRole())
        painter.fillRect(self.rect(), bgColor)
        
        # Calculate the progress width using the smooth value
        progress = self._smooth_value - self.minimum()
        total = self.maximum() - self.minimum()
        progressWidth = progress * self.width() / total
        
        # Create and set up the gradient
        gradient = QLinearGradient(self._offset, 0, self._offset + self._gradient_width, 0)
        gradient.setColorAt(0, QColor("#7700b3"))
        gradient.setColorAt(0.5, QColor("#ff69b4"))
        gradient.setColorAt(1, QColor("#7700b3"))
        
        # Draw the progress bar
        progressRect = QRect(0, 0, int(progressWidth), self.height())
        painter.fillRect(progressRect, gradient)

    def showEvent(self, event):
        super().showEvent(event)
        self._timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._timer.stop()

    def setAnimationSpeed(self, speed):
        self._animation_speed = speed

    def animationSpeed(self):
        return self._animation_speed

    def setAnimationFrequency(self, frequency):
        self._animation_frequency = frequency

    def animationFrequency(self):
        return self._animation_frequency

    def setGradientWidth(self, width):
        self._gradient_width = width

    def gradientWidth(self):
        return self._gradient_width

    animationSpeed = Property(float, animationSpeed, setAnimationSpeed)
    animationFrequency = Property(float, animationFrequency, setAnimationFrequency)
    gradientWidth = Property(int, gradientWidth, setGradientWidth)