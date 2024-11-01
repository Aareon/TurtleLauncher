from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QCheckBox, QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPoint, Signal, QRect
from pathlib import Path
from loguru import logger
from turtlelauncher.widgets.tabs import CustomTabWidget
from turtlelauncher.utils.color import parse_color

class BaseDialog(QDialog):
    def __init__(self, parent=None, title="", message="", icon_path=None, custom_styles=None, modal=True, resizable=False, flags=Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint):
        if resizable:
            flags |= Qt.WindowType.WindowMaximizeButtonHint
        super().__init__(parent, flags)
        self.setWindowTitle(title)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(modal)
        self.master = parent

        self.dragging = False
        self.drag_position = QPoint()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("content-widget")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        self.tab_widget = None
        self.settings = {}
        self.buttons = {}

        self.setup_ui(title, message, icon_path)
        self.layout.addWidget(self.content_widget)

        self.setStyleSheet(self.generate_stylesheet(custom_styles))

        if resizable:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
            self.maximize_button = QPushButton("□", self)
            self.maximize_button.setObjectName("maximize-button")
            self.maximize_button.clicked.connect(self.toggle_maximize)
            self.title_bar_layout.addWidget(self.maximize_button)


    def setup_ui(self, title, message, icon_path):
        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.setContentsMargins(10, 10, 10, 0)
        self.content_layout.addLayout(self.title_bar_layout)

        self.add_close_button()
        self.add_icon(icon_path)
        self.add_title(title)
        self.add_message(message)
    
    def get_setting(self, setting_name):
        if setting_name in self.settings:
            return self.settings[setting_name].isChecked()
        return None

    def set_setting(self, setting_name, value):
        if setting_name in self.settings:
            self.settings[setting_name].setChecked(value)

    def add_close_button(self):
        close_button = QPushButton("×", self)
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.reject)
        self.title_bar_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def add_icon(self, icon_path):
        if icon_path:
            logo = QLabel(self.content_widget)
            icon_path = Path(icon_path)
            if icon_path.exists():
                logo_pixmap = QPixmap(str(icon_path)).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo.setPixmap(logo_pixmap)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(logo)

    def add_title(self, title):
        title_label = QLabel(title, self.content_widget)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title-label")
        self.content_layout.addWidget(title_label)

    def add_message(self, message, color=None):
        if isinstance(message, str):
            message_label = QLabel(message, self.content_widget)
            message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message_label.setObjectName("message-label")
            message_label.setWordWrap(True)
            if color:
                message_label.setStyleSheet(f"color: {parse_color(color)};")
            self.content_layout.addWidget(message_label)
        elif isinstance(message, list):
            for idx, msg in enumerate(message):
                msg_label = QLabel(msg, self.content_widget)
                msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                msg_label.setObjectName(f"message-label-{idx}")
                msg_label.setWordWrap(True)
                if color:
                    msg_label.setStyleSheet(f"color: {parse_color(color)};")
                self.content_layout.addWidget(msg_label)
    
    def create_tab_widget(self):
        if not self.tab_widget:
            self.tab_widget = CustomTabWidget(self.content_widget)
            self.tab_widget.setObjectName("tab-widget")
            self.content_layout.addWidget(self.tab_widget)
        return self.tab_widget

    def create_checkbox(self, text, setting_name, initial_state=False, layout=None):
        checkbox = QCheckBox(text, self)
        checkbox.setObjectName("settings-checkbox")
        checkbox.setChecked(initial_state)
        checkbox.stateChanged.connect(lambda state: self.on_checkbox_changed(setting_name, state))
        self.settings[setting_name] = checkbox
        if layout:
            layout.addWidget(checkbox)
        return checkbox

    def on_checkbox_changed(self, setting_name, state):
        is_checked = state == Qt.CheckState.Checked.value
        logger.debug(f"Setting '{setting_name}' changed: {is_checked}")
        self.setting_changed.emit(setting_name, is_checked)

    def create_button(self, text, function, layout=None, object_name=None):
        button = QPushButton(text, self)
        if object_name:
            button.setObjectName(object_name)
        button.clicked.connect(function)
        if layout:
            layout.addWidget(button)
        self.buttons[text] = button  # Store the button in the buttons dictionary
        return button

    def generate_stylesheet(self, custom_styles=None):
        base_stylesheet = """
            #content-widget {
                background-color: rgba(44, 47, 51, 230);
                border: 2px solid #7289DA;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            #title-label {
                font-size: 18px;
                margin: 10px 0;
            }
            QPushButton {
                background-color: #7289DA;
                color: white;
                border: none;
                padding: 10px;
                margin: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5B6EAE;
            }
            #close-button {
                background-color: transparent;
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin: 5px;
                padding: 0;
            }
            #close-button:hover {
                color: #FF5555;
            }
            #settings-checkbox {
                color: white;
                font-size: 14px;
                padding: 5px 0;
            }
            #settings-checkbox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #7289DA;
                border-radius: 4px;
                background-color: #2C2F33;
            }
            #settings-checkbox::indicator:checked {
                background-color: #7289DA;
                image: url(check.png);
            }
            #settings-checkbox::indicator:hover {
                border-color: #5B6EAE;
            }
        """
        
        if custom_styles:
            for selector, style in custom_styles.items():
                base_stylesheet += f"\n{selector} {{\n"
                for property, value in style.items():
                    base_stylesheet += f"    {property}: {value};\n"
                base_stylesheet += "}\n"
        
        return base_stylesheet

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        logger.debug(f"{self.__class__.__name__} showEvent triggered")
        self.center_on_parent()
    
    def ensure_on_screen(self, dialog_geometry: QRect, screen_geometry: QRect) -> QRect:
        """Ensure the dialog is fully visible on the screen."""
        if not screen_geometry.contains(dialog_geometry):
            # Left edge
            if dialog_geometry.left() < screen_geometry.left():
                dialog_geometry.moveLeft(screen_geometry.left())
            # Right edge
            if dialog_geometry.right() > screen_geometry.right():
                dialog_geometry.moveRight(screen_geometry.right())
            # Top edge
            if dialog_geometry.top() < screen_geometry.top():
                dialog_geometry.moveTop(screen_geometry.top())
            # Bottom edge
            if dialog_geometry.bottom() > screen_geometry.bottom():
                dialog_geometry.moveBottom(screen_geometry.bottom())
        return dialog_geometry

    def center_on_parent(self):
        # Get the primary screen's geometry
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        
        # Get the dialog's geometry
        dialog_geometry = self.frameGeometry()
        
        if isinstance(self.master, QWidget):
            # If master is a widget, center on it
            parent_geometry = self.master.geometry()
            center_point = parent_geometry.center()
        else:
            # If master is not a widget (e.g., QApplication), center on screen
            center_point = screen_geometry.center()
        
        # Move dialog to center point
        dialog_geometry.moveCenter(center_point)
        
        # Ensure the dialog is fully visible on the screen
        dialog_geometry = self.ensure_on_screen(dialog_geometry, screen_geometry)
        
        # Set the new position
        self.move(dialog_geometry.topLeft())
        logger.debug(f"Centered dialog at: {dialog_geometry.topLeft()}")

    def closeEvent(self, event):
        logger.debug(f"{self.__class__.__name__} closeEvent triggered")
        super().closeEvent(event)