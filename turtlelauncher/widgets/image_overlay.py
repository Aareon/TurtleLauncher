from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QHBoxLayout
from PySide6.QtGui import QPainter, QWheelEvent, QTransform
from PySide6.QtCore import Qt, Signal

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setStyleSheet("background: transparent;")

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.15
        if event.angleDelta().y() < 0:
            zoom_factor = 1.0 / zoom_factor
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

class ImageOverlay(QWidget):
    closed = Signal()

    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: rgba(0, 0, 0, 180);")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # GraphicsView for the image
        self.view = ZoomableGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())

        main_layout.addWidget(self.view)

        # Close button
        self.close_button = QPushButton("Close", self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(218, 0, 255, 0.7);
                color: white;
                border: 2px solid white;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: rgba(161, 0, 188, 0.9);
                border-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: rgba(128, 0, 150, 1.0);
            }
        """)
        self.close_button.clicked.connect(self.close)

        # Position the close button
        self.position_close_button()

        # Connect the view's resize event to reposition the button
        self.view.resizeEvent = self.custom_resize_event

    def position_close_button(self):
        button_margin = 10
        button_x = (self.view.width() - self.close_button.width()) // 2
        self.close_button.move(button_x, button_margin)

    def custom_resize_event(self, event):
        super(ZoomableGraphicsView, self.view).resizeEvent(event)
        self.position_close_button()
        self.fit_image_in_view()

    def showEvent(self, event):
        super().showEvent(event)
        self.fit_image_in_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_image_in_view()
        self.position_close_button()

    def fit_image_in_view(self):
        view_size = self.view.viewport().size()
        scene_rect = self.scene.sceneRect()
        scale = min(view_size.width() / scene_rect.width(),
                    view_size.height() / scene_rect.height())
        self.view.setTransform(QTransform().scale(scale, scale))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.view.geometry().contains(event.pos()):
            self.close()

    def close(self):
        super().close()
        self.closed.emit()