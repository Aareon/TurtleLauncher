from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QHBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QColor, QWheelEvent, QCursor, QTransform
from PySide6.QtCore import Qt, QRectF, Signal, QPointF, QSize

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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top bar for close button
        top_bar = QWidget()
        top_bar.setStyleSheet("background: transparent;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)

        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0.5);
                color: white;
                border: none;
                font-size: 24px;
                padding: 5px;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.7);
            }
        """)
        close_button.clicked.connect(self.close)
        top_layout.addStretch()
        top_layout.addWidget(close_button)

        main_layout.addWidget(top_bar)

        # GraphicsView for the image
        self.view = ZoomableGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())

        main_layout.addWidget(self.view)

    def showEvent(self, event):
        super().showEvent(event)
        self.fit_image_in_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_image_in_view()

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