import cv2
import numpy as np
import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from utils.camera_manager import CameraManager # 👈 Imported Manager


class CalibrationScreen(QWidget):
    def __init__(self):
        super().__init__()

        # ---------------- WINDOW ----------------
        self.setWindowTitle("Calibration")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        self.is_person = False
        self.is_light = False
        self.cap = None
        self.camera_ready_flag = False  

        base_dir = os.path.dirname(os.path.dirname(__file__))

        # ======================================================
        # BACKGROUND (FIXED)
        # ======================================================
        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())

        bg_path = os.path.join(base_dir, "assets", "background.jpg")
        bg_img = cv2.imread(bg_path)
        bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB)
        bg_img = cv2.GaussianBlur(bg_img, (25, 25), 0)

        self.bg_raw = bg_img  
        self.update_background()
        self.bg.lower()

        # ======================================================
        # HEADER
        # ======================================================
        self.header = QLabel("🤖 AI PERSONAL TRAINER")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("""
            font-size:20px;
            font-weight:bold;
            padding:12px;
            color:white;
            background-color:rgba(30, 41, 59, 200);
            border-radius:12px;
        """)

        self.sub = QLabel("Calibration ensures accurate AI pose tracking before workout")
        self.sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub.setStyleSheet("""
            font-size:12px;
            color:#cbd5e1;
        """)

        # ======================================================
        # CAMERA
        # ======================================================
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(400, 350)
        self.camera_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("""
            background-color:rgba(11, 18, 32, 200);
            border:2px solid #1e293b;
            border-radius:18px;
            color: #38bdf8;
            font-weight: bold;
        """)
        self.camera_label.setText("Initializing Camera...")

        # ======================================================
        # RIGHT PANEL
        # ======================================================
        self.person_card = QLabel("● Person Detection")
        self.light_card = QLabel("● Lighting Check")
        self.person_card.setStyleSheet(self.gray_card())
        self.light_card.setStyleSheet(self.gray_card())

        self.btn = QPushButton("Select Exercise")
        self.btn.setEnabled(False)
        self.btn.setFixedHeight(45)
        self.btn.setFixedWidth(240)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color:#334155;
                color:white;
                border-radius:10px;
                font-weight:bold;
            }
            QPushButton:enabled {
                background-color:#38bdf8;
                color:black;
                font-weight:bold;
            }
            QPushButton:hover {
                background-color: #0ea5e9;
            }
        """)

        self.tip = QLabel(
            "Tip:\n"
            "• Stand 1–2 meters away\n"
            "• Ensure bright lighting\n"
            "• Keep full body visible"
        )
        self.tip.setStyleSheet("""
            font-size:12px;
            color:#cbd5e1;
            background-color:rgba(30, 41, 59, 200);
            padding:14px;
            border-radius:12px;
        """)
        self.tip.setFixedWidth(240)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addStretch()
        right_layout.addWidget(self.person_card)
        right_layout.addWidget(self.light_card)
        right_layout.addSpacing(12)
        right_layout.addWidget(self.tip)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.btn)
        right_layout.addStretch()
        right_widget.setLayout(right_layout)

        # ======================================================
        # MAIN LAYOUT
        # ======================================================
        body_layout = QHBoxLayout()
        body_layout.addStretch()
        body_layout.addWidget(self.camera_label)
        body_layout.addSpacing(25)
        body_layout.addWidget(right_widget)
        body_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.sub)
        main_layout.addSpacing(10)
        main_layout.addLayout(body_layout)
        self.setLayout(main_layout)

    def activate_camera_stream(self):
        self.cap = CameraManager.get_camera()
        if self.cap is not None:
            self.camera_ready_flag = True
            self.camera_label.setText("Camera Connected!")
            self.start_timer_logic() # Timer ko bhi yahan chalu krwa dein
        else:
            self.camera_label.setText("❌ Error: Camera Hardware not found.")

    def start_timer_logic(self):
        if not hasattr(self, "timer"):
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)

    def showEvent(self, event):
        super().showEvent(event)
        if self.camera_ready_flag:
            self.start_timer_logic()

    def update_background(self):
        h, w, ch = self.bg_raw.shape
        qt_img = QImage(self.bg_raw.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.bg.setPixmap(
            QPixmap.fromImage(qt_img).scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def resizeEvent(self, event):
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.update_background()
        super().resizeEvent(event)

    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            self.is_light = np.mean(gray) > 80
            self.is_person = np.std(gray) > 20

            if self.is_person:
                self.person_card.setText("✔ Person Detected")
                self.person_card.setStyleSheet(self.green_card())
            else:
                self.person_card.setText("● No Person Detected")
                self.person_card.setStyleSheet(self.gray_card())

            if self.is_light:
                self.light_card.setText("✔ Good Lighting")
                self.light_card.setStyleSheet(self.green_card())
            else:
                self.light_card.setText("● Poor Lighting")
                self.light_card.setStyleSheet(self.gray_card())

            self.btn.setEnabled(bool(self.is_person and self.is_light))

            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(img))

    def green_card(self):
        return """
            font-size:15px;
            padding:16px;
            background-color:#14532d;
            color:#22c55e;
            border-radius:14px;
        """

    def gray_card(self):
        return """
            font-size:15px;
            padding:16px;
            background-color:rgba(30, 41, 59, 200);
            color:white;
            border-radius:14px;
        """

    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()