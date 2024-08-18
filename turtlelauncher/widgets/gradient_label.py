from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QLinearGradient, QPainter, QPen, QColor
from PySide6.QtCore import Qt

class GradientLabel(QLabel):
    def __init__(self, text, color_one: QColor, color_two: QColor, vertical=False, intensity=1.0, anti_aliasing=True, parent=None):
        super().__init__(text, parent)
        self.vertical = vertical
        self.color_one = color_one
        self.color_two = color_two
        self.intensity = max(0.0, intensity)
        self.anti_aliasing = anti_aliasing

    def interpolate_color(self, color1: QColor, color2: QColor, factor: float) -> QColor:
        r = max(0, min(255, int(color1.red() + factor * (color2.red() - color1.red()))))
        g = max(0, min(255, int(color1.green() + factor * (color2.green() - color1.green()))))
        b = max(0, min(255, int(color1.blue() + factor * (color2.blue() - color1.blue()))))
        a = max(0, min(255, int(color1.alpha() + factor * (color2.alpha() - color1.alpha()))))
        return QColor(r, g, b, a)

    def extrapolate_color(self, color1: QColor, color2: QColor, factor: float) -> QColor:
        r = max(0, min(255, int(color2.red() + factor * (color2.red() - color1.red()))))
        g = max(0, min(255, int(color2.green() + factor * (color2.green() - color1.green()))))
        b = max(0, min(255, int(color2.blue() + factor * (color2.blue() - color1.blue()))))
        a = max(0, min(255, int(color2.alpha() + factor * (color2.alpha() - color1.alpha()))))
        return QColor(r, g, b, a)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.anti_aliasing:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.TextAntialiasing)
        else:
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.setRenderHint(QPainter.TextAntialiasing, False)

        painter.setFont(self.font())

        if self.vertical:
            self.gradient = QLinearGradient(0, 0, 0, self.height())
        else:
            self.gradient = QLinearGradient(0, 0, self.width(), 0)

        if self.intensity <= 1.0:
            start_color = self.interpolate_color(self.color_one, self.color_two, self.intensity / 2)
            end_color = self.interpolate_color(self.color_one, self.color_two, (self.intensity + 1) / 2)
        else:
            start_color = self.color_one
            end_color = self.extrapolate_color(self.color_one, self.color_two, self.intensity - 1)

        self.gradient.setColorAt(0, start_color)
        self.gradient.setColorAt(1, end_color)

        painter.setPen(QPen(self.gradient, 2))
        painter.drawText(self.rect(), self.alignment(), self.text())

    def set_anti_aliasing(self, enabled: bool):
        self.anti_aliasing = enabled
        self.update()  # Trigger a repaint

    def is_anti_aliasing(self) -> bool:
        return self.anti_aliasing