from PySide6.QtWidgets import (QVBoxLayout, QFrame, QWidget, QPushButton, 
                               QHBoxLayout, QStyle, QSlider, QCheckBox)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QKeyEvent

class VideoPlayer(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self.setMouseTracking(True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)

        self.controls_widget = QWidget()
        self.controls_layout = QHBoxLayout(self.controls_widget)
        self.layout.addWidget(self.controls_widget)

        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)

        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.sliderMoved.connect(self.set_position)

        self.volume_button = QPushButton()
        self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.volume_button.clicked.connect(self.toggle_mute)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.fullscreen_button = QPushButton()
        self.fullscreen_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        self.always_show_controls = QCheckBox("Always Show Controls")
        self.always_show_controls.stateChanged.connect(self.toggle_controls_visibility)

        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.seek_slider)
        self.controls_layout.addWidget(self.volume_button)
        self.controls_layout.addWidget(self.volume_slider)
        self.controls_layout.addWidget(self.fullscreen_button)
        self.controls_layout.addWidget(self.always_show_controls)

        self.fade_timer = QTimer(self)
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self.fade_out_controls)

        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
            QPushButton {
                background-color: rgba(74, 14, 78, 150);
                color: #FFD700;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(106, 26, 110, 200);
            }
        """)

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def set_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
        self.seek_slider.setValue(position)

    def duration_changed(self, duration):
        self.seek_slider.setRange(0, duration)

    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100)

    def toggle_mute(self):
        self.audio_output.setMuted(not self.audio_output.isMuted())

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def toggle_controls_visibility(self, state):
        self.controls_widget.setVisible(state == Qt.Checked)

    def fade_out_controls(self):
        if not self.always_show_controls.isChecked():
            self.controls_widget.setVisible(False)

    def enterEvent(self, event):
        self.controls_widget.setVisible(True)
        self.fade_timer.start(3000)

    def leaveEvent(self, event):
        self.fade_out_controls()

    def mouseMoveEvent(self, event):
        self.controls_widget.setVisible(True)
        self.fade_timer.start(3000)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space:
            self.play_pause()
        elif event.key() == Qt.Key_F:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_M:
            self.toggle_mute()
        elif event.key() == Qt.Key_Right:
            self.media_player.setPosition(self.media_player.position() + 5000)  # Forward 5 seconds
        elif event.key() == Qt.Key_Left:
            self.media_player.setPosition(self.media_player.position() - 5000)  # Backward 5 seconds
        else:
            super().keyPressEvent(event)

    def set_media(self, url):
        self.media_player.setSource(QUrl(url))

    def play(self):
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()