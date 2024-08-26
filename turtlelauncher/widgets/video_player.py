import cv2
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QStyle
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor

class VideoThread(QThread):
    change_pixmap_signal = Signal(QImage)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.cap = None
        self.current_frame = 0
        self.total_frames = 0

    def run(self):
        while self._run_flag:
            ret, cv_img = self.cap.read()
            if ret:
                self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(convert_to_Qt_format)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def stop(self):
        self._run_flag = False
        self.wait()

    def pause(self):
        self._run_flag = False

    def resume(self):
        self._run_flag = True
        self.start()

    def set_video(self, video_path):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def seek(self, frame_number):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

class OpenCVVideoPlayer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setLineWidth(0)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1d24;
                border-radius: 10px;
            }
            QPushButton {
                background-color: rgba(74, 14, 78, 150);
                color: #FFD700;
                border: none;
                border-radius: 15px;
                padding: 5px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(106, 26, 110, 200);
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF539C, stop:1 #FFD700);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label, 1)

        self.create_controls()

        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start()

    def create_controls(self):
        controls_layout = QHBoxLayout()

        self.prev_button = QPushButton("←")
        self.prev_button.setFixedSize(40, 40)
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.setFixedSize(40, 40)
        self.next_button = QPushButton("→")
        self.next_button.setFixedSize(40, 40)

        self.play_button.clicked.connect(self.play_pause)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.position_slider)

        self.layout.addLayout(controls_layout)

    def set_media(self, video_path):
        self.thread.set_video(video_path)

    def play_pause(self):
        if self.thread.isRunning():
            self.thread.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.thread.resume()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def set_position(self, position):
        if self.thread.total_frames > 0:
            frame_number = int((position / 1000) * self.thread.total_frames)
            self.thread.seek(frame_number)

    def update_slider(self):
        if self.thread.total_frames > 0:
            position = int((self.thread.current_frame / self.thread.total_frames) * 1000)
            self.position_slider.setValue(position)

    def update_image(self, image):
        scaled_image = image.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(QPixmap.fromImage(scaled_image))

    def play(self):
        self.thread.start()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def pause(self):
        self.thread.pause()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def stop(self):
        self.thread.stop()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.video_label.setFixedSize(self.size())

    def connect_navigation_buttons(self, prev_callback, next_callback):
        self.prev_button.clicked.connect(prev_callback)
        self.next_button.clicked.connect(next_callback)