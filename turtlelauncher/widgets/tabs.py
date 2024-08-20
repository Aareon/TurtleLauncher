from PySide6.QtWidgets import QTabBar, QStyleOptionTab, QTabWidget, QHBoxLayout
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QSize

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setExpanding(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            
            if self.currentIndex() == index:
                painter.setBrush(QColor("#7289DA"))  # Active tab color
            else:
                painter.setBrush(QColor("#2C2F33"))  # Inactive tab color
            
            painter.setPen(Qt.NoPen)
            painter.drawRect(tabRect)
            
            # Draw the text
            if self.currentIndex() == index:
                painter.setPen(QColor("#FFFFFF"))  # White text for active tab
            else:
                painter.setPen(QColor("#99AAB5"))  # Light gray text for inactive tab
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(tabRect, Qt.AlignCenter, self.tabText(index))

    def tabSizeHint(self, index):
        return QSize(100, 40)  # Adjust the size to match other elements

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))
        
        # Create a horizontal layout to center the tab bar
        self.tab_layout = QHBoxLayout(self)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.addStretch()
        self.tab_layout.addWidget(self.tabBar())
        self.tab_layout.addStretch()
        
        # Set the tab bar to the top of the widget
        self.setTabPosition(QTabWidget.North)
        
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
                padding-top: 10px;  /* Add some space below the tabs */
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)