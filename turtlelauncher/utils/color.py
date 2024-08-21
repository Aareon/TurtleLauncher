from PySide6.QtGui import QColor
from loguru import logger


def parse_color(color):
    if isinstance(color, str):
        if color.startswith('#'):
            return color  # Hex color code
        else:
            # Try to parse as a named color
            qcolor = QColor(color)
            if qcolor.isValid():
                return qcolor.name()
    elif isinstance(color, (tuple, list)):
        if len(color) == 3:
            return f"rgb{color}"
        elif len(color) == 4:
            return f"rgba{color}"
    
    # If parsing fails, return a default color
    logger.warning(f"Invalid color format: {color}. Using default color.")
    return "#FFFFFF"