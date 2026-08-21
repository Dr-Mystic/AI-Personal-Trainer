from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
import os
from utils.camera_manager import CameraManager  # 👈 Imported manager

class SplashScreen(QWidget):
    start_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        # ---------------- WINDOW ----------------
        self.setWindowTitle("AI Personal Trainer")
        self.resize(1000, 700)   
        self.setMinimumSize(800, 600)

        base_dir = os.path.dirname(os.path.dirname(__file__))

        # ======================================================
        # BACKGROUND IMAGE
        # ======================================================
        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        bg_path = os.path.join(base_dir, "assets", "background.jpg")  
        self.bg_pixmap = QPixmap(bg_path)
        self.update_background()
        self.bg.lower()

        # ---------------- STYLE ----------------
        self.setStyleSheet("background: transparent;")

        # ---------------- LAYOUT ----------------
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------- LOGO ----------------
        self.logo = QLabel()
        logo_path = os.path.join(base_dir, "assets", "logo.png")
        pixmap = QPixmap(logo_path)
        self.logo.setPixmap(pixmap.scaled(
            300, 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------- TITLE ----------------
        self.title = QLabel("AI Personal Trainer")
        self.title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.title.setStyleSheet("color: white;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------- SUBTITLE ----------------
        self.subtitle = QLabel("Train smarter. Move better.")
        self.subtitle.setFont(QFont("Segoe UI", 17))
        self.subtitle.setStyleSheet("color: #94a3b8;")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------- DESCRIPTION ----------------
        self.description = QLabel(
            "Real-time biomechanical analysis powered by AI.\n"
            "Perfect your form, prevent injuries, and maximize every rep."
        )
        self.description.setFont(QFont("Segoe UI", 14))
        self.description.setStyleSheet("color: #cbd5f5;")
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------- PROGRESS BAR ----------------
        self.progress = QProgressBar()
        self.progress.setFixedSize(600, 17)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(30, 41, 59, 180);
                border-radius: 6px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #38bdf8;
                border-radius: 6px;
            }
        """)

        # ---------------- BUTTON ----------------
        self.start_btn = QPushButton("Start Session")
        self.start_btn.setFixedSize(300, 50)
        self.start_btn.setVisible(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #38bdf8;
                color: black;
                font-weight: bold;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #0ea5e9;
            }
        """)
        self.start_btn.clicked.connect(self.start_clicked.emit)

        # ---------------- ADD WIDGETS ----------------
        self.layout.addWidget(self.logo)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.title)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.subtitle)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.description)
        self.layout.addSpacing(40)
        self.layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

        # 🚀 REAL INTERACTION: Trigger background camera preloading right away!
        CameraManager.start_preload(self.on_progress_changed, self.on_camera_loaded)

    def resizeEvent(self, event):
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        if self.bg_pixmap:
            scaled = self.bg_pixmap.scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg.setPixmap(scaled)
    
    # 💥 INSTEAD OF FAKE TIMER, TRACK ACTUAL HARDWARE LOADING STATUS
    def on_progress_changed(self, value):
        self.progress.setValue(value)

    def on_camera_loaded(self, cap_object):
        # Jaise hi background hardware call handle ho jaye, layout switch open krdo
        self.progress.setVisible(False)
        self.start_btn.setVisible(True)