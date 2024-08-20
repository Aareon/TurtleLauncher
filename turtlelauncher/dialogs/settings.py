from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, 
                               QCheckBox, QHBoxLayout)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPoint, Signal
from pathlib import Path
from loguru import logger
from turtlelauncher.dialogs.binary_select import BinarySelectionDialog

class SettingsDialog(QDialog):
    particles_setting_changed = Signal(bool)

    def __init__(self, parent=None, game_installed=False, config=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Turtle WoW Settings")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.game_installed = game_installed
        self.config = config

        logger.debug(f"Game installed: {self.game_installed}")
        logger.debug(f"Particles disabled: {self.config.particles_disabled}")
        logger.debug(f"Config: {self.config}")

        self.dragging = False
        self.drag_position = QPoint()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        content_widget = QWidget(self)
        content_widget.setObjectName("content-widget")
        content_layout = QVBoxLayout(content_widget)

        # Logo
        logo = QLabel(content_widget)
        logo_path = Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png"
        if logo_path.exists():
            logo_pixmap = QPixmap(str(logo_path)).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo)

        # Title
        title = QLabel("Turtle WoW Settings", content_widget)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title-label")
        content_layout.addWidget(title)

        # Buttons
        self.clear_addon_settings_button = self.create_button("Clear Addon Settings", self.clear_addon_settings, content_layout)
        self.clear_cache_button = self.create_button("Clear Cache", self.clear_cache, content_layout)
        self.open_install_directory_button = self.create_button("Open Install Directory", self.open_install_directory, content_layout)
        self.select_binary_button = self.create_button("Select Binary to Launch", self.select_binary, content_layout)

        # Update button states
        self.update_button_states()

        # Particles checkbox
        self.particles_checkbox = QCheckBox("Disable Particles", self)
        self.particles_checkbox.setObjectName("particles-checkbox")
        self.particles_checkbox.setChecked(self.config.particles_disabled)
        content_layout.addWidget(self.particles_checkbox)

        # Close button
        close_button = QPushButton("×", content_widget)
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.close)

        # Add close button to top-right corner
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        content_layout.insertLayout(0, button_layout)

        layout.addWidget(content_widget)

        self.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #4A5162;
                color: #8E9297;
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
            QCheckBox {
                color: white;
                font-size: 14px;
                margin: 10px 20px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #7289DA;
                border-radius: 4px;
                background-color: rgba(44, 47, 51, 230);
            }
            QCheckBox::indicator:checked {
                background-color: #7289DA;
                image: url(check.png);
            }
            QCheckBox::indicator:hover {
                border-color: #5B6EAE;
            }
        """)

    def create_button(self, text, function, layout):
        button = QPushButton(text, self)
        button.clicked.connect(function)
        layout.addWidget(button)
        return button

    def update_button_states(self):
        buttons = [
            self.clear_addon_settings_button,
            self.clear_cache_button,
            self.open_install_directory_button,
            self.select_binary_button
        ]
        for button in buttons:
            button.setEnabled(self.game_installed)

    def clear_addon_settings(self):
        logger.debug("Clearing addon settings")
        # Implement addon settings clearing logic here

    def clear_cache(self):
        logger.debug("Clearing cache")
        # Implement cache clearing logic here

    def open_install_directory(self):
        logger.debug("Opening install directory")
        # Implement directory opening logic here

    def select_binary(self):
        binary_dialog = BinarySelectionDialog(self.config, self)
        if binary_dialog.exec() == QDialog.DialogCode.Accepted:
            logger.debug("Binary selected from custom dialog")

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
        # Update checkbox state when dialog is shown
        self.particles_checkbox.setChecked(self.config.particles_disabled)

    def closeEvent(self, event):
        # Save the particles setting when the dialog is closed
        self.save_particles_setting()
        super().closeEvent(event)

    def save_particles_setting(self):
        is_checked = self.particles_checkbox.isChecked()
        if is_checked != self.config.particles_disabled:
            logger.debug(f"Saving particles setting: {is_checked}")
            self.config.particles_disabled = is_checked
            self.config.save()
            self.particles_setting_changed.emit(is_checked)