from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QCheckBox,
    QPushButton, QLineEdit, QComboBox, QLabel, QInputDialog, QMessageBox,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QIcon
from pathlib import Path
import json
import httpx
from datetime import datetime
from turtlelauncher.dialogs.base import BaseDialog
from turtlelauncher.utils.globals import IMAGES, DATA

from loguru import logger

class AddonListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                background-color: #2C2F33;
                border: 1px solid #7289DA;
                border-radius: 5px;
            }
            QListWidget::item {
                color: #FFFFFF;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #7289DA;
            }
        """)

class AddonItem(QFrame):
    stateChanged = Signal(str, bool)

    def __init__(self, addon_name, addon_info, parent=None):
        super().__init__(parent)
        self.addon_name = addon_name
        self.addon_info = addon_info
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("AddonItem { background-color: transparent; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        self.checkbox = QCheckBox(addon_name)
        self.checkbox.setChecked(addon_info.get('enabled', False))
        self.checkbox.stateChanged.connect(self.on_state_changed)
        self.checkbox.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #7289DA;
                border-radius: 4px;
                background-color: #2C2F33;
            }
            QCheckBox::indicator:checked {
                background-color: #7289DA;
                image: url(check.png);
            }
            QCheckBox::indicator:unchecked:hover {
                border-color: #5B6EAE;
            }
        """)

        self.version_label = QLabel(f"v{addon_info.get('version', 'Unknown')}")
        self.version_label.setStyleSheet("color: #99AAB5;")

        self.update_button = QPushButton("Update")
        self.update_button.setFixedSize(60, 25)
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #43B581;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3CA374;
            }
        """)
        self.update_button.clicked.connect(self.check_for_update)

        layout.addWidget(self.checkbox, 1)
        layout.addWidget(self.version_label)
        layout.addWidget(self.update_button)

    def on_state_changed(self, state):
        self.stateChanged.emit(self.addon_name, state == Qt.Checked)

    def check_for_update(self):
        # Implement update checking logic here
        pass

class AddonManagerDialog(BaseDialog):
    def __init__(self, config, parent=None):
        self.config = config
        self.addons_file = DATA / "addons.json"
        self.addons = self.load_addons()
        super().__init__(
            parent=parent,
            title="Addon Manager",
            message="Manage your World of Warcraft addons",
            icon_path=str(IMAGES / "turtle_wow_icon.png"),
            modal=True,
            flags=Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint
        )

    def setup_ui(self, title, message, icon_path):
        super().setup_ui(title, message, icon_path)
        self.setup_additional_ui()
        
        # Add maximize button
        self.maximize_button = QPushButton("□")
        self.maximize_button.setObjectName("maximize-button")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        button_layout = self.findChild(QHBoxLayout)
        if button_layout:
            button_layout.insertWidget(button_layout.count() - 1, self.maximize_button)

    def setup_additional_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        category_layout = QHBoxLayout()
        category_label = QLabel("Categories:")
        category_label.setStyleSheet("color: #FFFFFF;")
        self.category_combo = QComboBox()
        self.style_combo_box(self.category_combo)
        categories = set(addon.get('category', 'Uncategorized') for addon in self.addons)
        self.category_combo.addItems(["All"] + list(categories))
        self.category_combo.currentTextChanged.connect(self.filter_addons)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        main_layout.addLayout(category_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search addons...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2C2F33;
                color: #FFFFFF;
                border: 1px solid #7289DA;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_addons)
        main_layout.addWidget(self.search_input)

        self.addon_list = AddonListWidget()
        main_layout.addWidget(self.addon_list)

        button_layout = QHBoxLayout()
        self.add_addon_button = QPushButton("Add Addon")
        self.remove_addon_button = QPushButton("Remove Addon")
        for button in [self.add_addon_button, self.remove_addon_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #7289DA;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5B6EAE;
                }
            """)
        self.add_addon_button.clicked.connect(self.add_addon)
        self.remove_addon_button.clicked.connect(self.remove_addon)
        button_layout.addWidget(self.add_addon_button)
        button_layout.addWidget(self.remove_addon_button)
        main_layout.addLayout(button_layout)

        self.content_layout.addLayout(main_layout)

        self.populate_addon_list()

    def style_combo_box(self, combo_box):
        combo_box.setStyleSheet("""
            QComboBox {
                background-color: #2C2F33;
                color: #FFFFFF;
                border: 1px solid #99AAB5;
                padding: 5px;
                border-radius: 3px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #99AAB5;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #7289DA;
            }
            QComboBox::down-arrow {
                image: url(path/to/dropdown_arrow.png);
            }
            QComboBox QAbstractItemView {
                background-color: #2C2F33;
                color: #FFFFFF;
                selection-background-color: #7289DA;
                border: 1px solid #99AAB5;
            }
        """)

    def load_addons(self):
        if self.addons_file.exists():
            with open(self.addons_file, 'r') as f:
                return json.load(f).get("addons", [])
        return []

    def save_addons(self):
        with open(self.addons_file, 'w') as f:
            json.dump({"addons": self.addons}, f, indent=2)

    def populate_addon_list(self):
        self.addon_list.clear()
        for addon in self.addons:
            item = QListWidgetItem(self.addon_list)
            addon_widget = AddonItem(addon['name'], addon)
            addon_widget.stateChanged.connect(self.on_addon_state_changed)
            item.setSizeHint(addon_widget.sizeHint())
            self.addon_list.addItem(item)
            self.addon_list.setItemWidget(item, addon_widget)

    def filter_addons(self):
        category = self.category_combo.currentText()
        search_text = self.search_input.text().lower()

        for i in range(self.addon_list.count()):
            item = self.addon_list.item(i)
            addon_widget = self.addon_list.itemWidget(item)
            addon_name = addon_widget.addon_name
            addon_info = next((addon for addon in self.addons if addon['name'] == addon_name), None)

            if addon_info:
                category_match = category == "All" or addon_info.get('category', 'Uncategorized') == category
                search_match = search_text in addon_name.lower()

                item.setHidden(not (category_match and search_match))

    def on_addon_state_changed(self, addon_name, state):
        for addon in self.addons:
            if addon['name'] == addon_name:
                addon['enabled'] = state
                break
        self.save_addons()

    def add_addon(self):
        addon_name, ok = QInputDialog.getText(self, "Add Addon", "Enter addon name:")
        if ok and addon_name:
            categories = set(addon.get('category', 'Uncategorized') for addon in self.addons)
            category, ok = QInputDialog.getItem(self, "Select Category", "Choose addon category:", 
                                                list(categories) or ["Uncategorized"], 
                                                0, True)
            if ok:
                source_type, ok = QInputDialog.getItem(self, "Source Type", "Select addon source type:",
                                                       ["Download Link", "GitHub Repository"], 0, False)
                if ok:
                    if source_type == "Download Link":
                        source, ok = QInputDialog.getText(self, "Download Link", "Enter addon download link:")
                    else:
                        source, ok = QInputDialog.getText(self, "GitHub Repository", "Enter GitHub repository URL:")
                    
                    if ok and source:
                        new_addon = {
                            'name': addon_name,
                            'category': category,
                            'source_type': source_type,
                            'source': source,
                            'enabled': False,
                            'version': 'Unknown',
                            'last_updated': datetime.now().isoformat()
                        }
                        self.addons.append(new_addon)
                        self.save_addons()
                        self.populate_addon_list()
                        self.filter_addons()

    def remove_addon(self):
        current_item = self.addon_list.currentItem()
        if current_item:
            addon_widget = self.addon_list.itemWidget(current_item)
            addon_name = addon_widget.addon_name
            reply = QMessageBox.question(self, "Remove Addon", 
                                         f"Are you sure you want to remove {addon_name}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.addons = [addon for addon in self.addons if addon['name'] != addon_name]
                self.save_addons()
                self.populate_addon_list()
                self.filter_addons()

    async def check_for_updates(self):
        async with httpx.AsyncClient() as client:
            for addon in self.addons:
                if addon['source_type'] == 'GitHub Repository':
                    repo_url = addon['source']
                    api_url = f"https://api.github.com/repos/{repo_url.split('github.com/')[-1]}/commits"
                    response = await client.get(api_url)
                    if response.status_code == 200:
                        latest_commit = response.json()[0]
                        latest_commit_date = latest_commit['commit']['author']['date']
                        if latest_commit_date > addon['last_updated']:
                            addon['version'] = latest_commit['sha'][:7]
                            addon['last_updated'] = latest_commit_date
                            # Implement update logic here
                elif addon['source_type'] == 'Download Link':
                    # Implement logic to check for updates from download link
                    pass

        self.save_addons()
        self.populate_addon_list()

    def generate_stylesheet(self, custom_styles=None):
        base_stylesheet = super().generate_stylesheet(custom_styles)
        additional_styles = """
            #maximize-button {
                background-color: transparent;
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin: 5px;
                padding: 0;
            }
            #maximize-button:hover {
                color: #7289DA;
            }
        """
        return base_stylesheet + additional_styles

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPosition)
            event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.setMinimumSize(500, 400)  # Set a smaller minimum size
        self.resize(600, 500)  # Set an initial size