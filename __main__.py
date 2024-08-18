import sys
from PySide6.QtWidgets import QApplication
from turtlelauncher.windows.main_window import TurtleWoWLauncher

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TurtleWoWLauncher()
    window.show()
    sys.exit(app.exec())