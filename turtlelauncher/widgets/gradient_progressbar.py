from PySide6.QtWidgets import QProgressBar
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QBrush, QPainterPath, QImage
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

class CrystalParticle(Particle):
    def __init__(self, pos, velocity, size, color, lifespan):
        super().__init__(pos, velocity, size, color, lifespan)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)

    def update(self):
        super().update()
        self.rotation += self.rotation_speed
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
        self._blur_width = 20  # Width of the blur effect
        self._particle_spawn_offset = 10  # Offset for particle spawn point

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_offset)

        self._smooth_value = 0.0
        
        # Particle system
        self._particles = []
        self._max_particles = 50
        self._particle_effect_active = False
        self._circular_particles_enabled = True
        self._crystal_particles_enabled = True

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
            particle_type = self._get_random_particle_type()
            if particle_type:
                self._particles.append(self._create_particle(particle_x, particle_type))

    def _get_random_particle_type(self):
        enabled_types = []
        if self._circular_particles_enabled:
            enabled_types.append("circular")
        if self._crystal_particles_enabled:
            enabled_types.append("crystal")
        
        if not enabled_types:
            return None
        return random.choice(enabled_types)

    def _create_particle(self, x, particle_type):
        # Offset the spawn point to cover the blurred edge
        spawn_x = x - self._particle_spawn_offset
        pos = QPointF(spawn_x, random.uniform(0, self.height()))
        velocity = QPointF(random.uniform(-2, 2), random.uniform(-2, 2))
        size = random.uniform(2, 6)
        color = QColor(random.randint(200, 255), random.randint(100, 200), random.randint(200, 255), 200)
        lifespan = random.randint(20, 40)

        if particle_type == "crystal":
            return CrystalParticle(pos, velocity, size * 1.5, color, lifespan * 1.25)
        else:
            return Particle(pos, velocity, size, color, lifespan)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create an image to draw on
        image = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        
        # Create a painter for the image
        imagePainter = QPainter(image)
        imagePainter.setRenderHint(QPainter.Antialiasing)
        
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
        imagePainter.fillRect(progressRect, gradient)

        # Create and draw the blur gradient
        blurGradient = QLinearGradient(progressWidth - self._blur_width, 0, progressWidth, 0)
        blurGradient.setColorAt(0, QColor(255, 255, 255, 255))
        blurGradient.setColorAt(1, QColor(255, 255, 255, 0))
        
        blurRect = QRect(int(progressWidth - self._blur_width), 0, self._blur_width, self.height())
        imagePainter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        imagePainter.fillRect(blurRect, blurGradient)
        
        imagePainter.end()
        
        # Draw the background
        bgColor = self.palette().color(self.backgroundRole())
        painter.fillRect(self.rect(), bgColor)
        
        # Draw the progress bar image
        painter.drawImage(0, 0, image)
        
        # Draw particles only if the effect is active
        if self._particle_effect_active:
            for particle in self._particles:
                if isinstance(particle, CrystalParticle):
                    self._draw_crystal(painter, particle)
                else:
                    painter.setBrush(QBrush(particle.color))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(particle.pos, particle.size, particle.size)

    def _draw_crystal(self, painter, crystal):
        painter.save()
        painter.translate(crystal.pos)
        painter.rotate(crystal.rotation)

        path = QPainterPath()
        path.moveTo(0, -crystal.size)
        path.lineTo(crystal.size * 0.5, 0)
        path.lineTo(0, crystal.size)
        path.lineTo(-crystal.size * 0.5, 0)
        path.closeSubpath()

        painter.setBrush(QBrush(crystal.color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        painter.restore()
    
    def _start_animation(self):
        if not self._timer.isActive():
            self._timer.start(16)  # Update every 16ms (approximately 60 FPS)

    def start_particle_effect(self):
        self._particle_effect_active = True
        self._start_animation()

    def stop_particle_effect(self):
        self._particle_effect_active = False
        self._particles.clear()
        # Keep the animation running for the progress bar
        self._start_animation()

    def set_circular_particles_enabled(self, enabled):
        self._circular_particles_enabled = enabled

    def set_crystal_particles_enabled(self, enabled):
        self._crystal_particles_enabled = enabled

    def showEvent(self, event):
        super().showEvent(event)
        self._start_animation()

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
    
    def set_blur_width(self, width):
        self._blur_width = max(0, width)  # Ensure non-negative value
        self.update()

    def blur_width(self):
        return self._blur_width

    blurWidth = Property(int, blur_width, set_blur_width)
    animationSpeed = Property(float, animationSpeed, setAnimationSpeed)
    gradientWidth = Property(int, gradientWidth, setGradientWidth)