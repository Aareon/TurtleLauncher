from PySide6.QtWidgets import QProgressBar
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QBrush
from PySide6.QtCore import QRect, QTimer, Qt, Property, QPointF
import random

class Particle:
    def __init__(self, pos, velocity, size, color, lifespan):
        self.pos = pos
        self.velocity = velocity
        self.size = size
        self.color = color
        self.lifespan = lifespan
        self.age = 0

    def update(self):
        self.pos += self.velocity
        self.age += 1
        return self.age < self.lifespan

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
        self._gradient_width = 600  # Width of one complete gradient cycle
        self._animation_speed = 1  # Pixels to move per frame

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_offset)

        self._smooth_value = 0.0
        
        # Particle system
        self._particles = []
        self._max_particles = 50
        self._particle_effect_active = False

    def _update_offset(self):
        # Update the offset
        self._offset += self._animation_speed
        if self._offset >= self._gradient_width:
            self._offset -= self._gradient_width

        # Smooth value update
        target_value = self.value()
        self._smooth_value += (target_value - self._smooth_value) * 0.1
        
        # Update particles only if the effect is active
        if self._particle_effect_active:
            self._update_particles()
        
        self.update()

    def _update_particles(self):
        # Update existing particles
        self._particles = [p for p in self._particles if p.update()]
        
        # Add new particles
        progress = self._smooth_value / self.maximum()
        particle_x = self.width() * progress
        if len(self._particles) < self._max_particles:
            self._particles.append(self._create_particle(particle_x))

    def _create_particle(self, x):
        pos = QPointF(x, random.uniform(0, self.height()))
        velocity = QPointF(random.uniform(-2, 2), random.uniform(-2, 2))
        size = random.uniform(2, 6)
        color = QColor(random.randint(200, 255), random.randint(100, 200), random.randint(200, 255), 200)
        lifespan = random.randint(20, 40)
        return Particle(pos, velocity, size, color, lifespan)

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
        gradient = QLinearGradient(0, 0, self._gradient_width, 0)
        gradient.setColorAt(0, QColor("#7700b3"))
        gradient.setColorAt(0.5, QColor("#ff69b4"))
        gradient.setColorAt(1, QColor("#7700b3"))
        
        # Set up the gradient translation
        gradient.setStart(-self._offset, 0)
        gradient.setFinalStop(self._gradient_width - self._offset, 0)
        
        # Enable gradient repeating
        gradient.setSpread(QLinearGradient.RepeatSpread)
        
        # Draw the progress bar
        progressRect = QRect(0, 0, int(progressWidth), self.height())
        painter.fillRect(progressRect, gradient)
        
        # Draw particles only if the effect is active
        if self._particle_effect_active:
            for particle in self._particles:
                painter.setBrush(QBrush(particle.color))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(particle.pos, particle.size, particle.size)

    def start_particle_effect(self):
        self._particle_effect_active = True
        self._timer.start(16)  # Update every 16ms (approximately 60 FPS)

    def stop_particle_effect(self):
        self._particle_effect_active = False
        self._particles.clear()
        self._timer.stop()

    def showEvent(self, event):
        super().showEvent(event)
        if self._particle_effect_active:
            self._timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._timer.stop()

    def setAnimationSpeed(self, speed):
        self._animation_speed = speed

    def animationSpeed(self):
        return self._animation_speed

    def setGradientWidth(self, width):
        self._gradient_width = width

    def gradientWidth(self):
        return self._gradient_width

    animationSpeed = Property(float, animationSpeed, setAnimationSpeed)
    gradientWidth = Property(int, gradientWidth, setGradientWidth)