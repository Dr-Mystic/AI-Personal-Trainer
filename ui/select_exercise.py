import cv2
import numpy as np
import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsBlurEffect
)
from exercises.biceps_screen import BicepsScreen
from exercises.squats_screen import SquatsScreen
from exercises.crunches_screen import CrunchesScreen
from ui.loading_dialog import LoadingDialog
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt6.QtGui import QImage, QPixmap


class SelectExercise(QWidget):
    def __init__(self, previous_screen=None):
        super().__init__()

        self.previous_screen = previous_screen

        # ---------------- WINDOW ----------------
        self.setWindowTitle("Select Exercise")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        base_dir = os.path.dirname(os.path.dirname(__file__))

        # ======================================================
        # BACKGROUND (FIXED WITH FAST TRANSFORMATION)
        # ======================================================
        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())

        bg_path = os.path.join(base_dir, "assets", "background.jpg")

        bg_img = cv2.imread(bg_path)
        bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB)
        bg_img = cv2.GaussianBlur(bg_img, (25, 25), 0)

        self.bg_raw = bg_img  # store original

        self.update_background()
        self.bg.lower()

        # ======================================================
        # HEADER
        # ======================================================
        self.header = QLabel("🤖 AI PERSONAL TRAINER")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            color:white;
            padding:16px;
            background-color:rgba(30, 41, 59, 200);
            border-radius:12px;
        """)

        self.sub = QLabel("Select an exercise to start AI tracking")
        self.sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub.setStyleSheet("""
            font-size:30px;
            color:#cbd5e1;
        """)

        # ======================================================
        # CARD FUNCTION WITH SAFE POSITION FLOATING ANIMATION
        # ======================================================
        def create_card(title, desc, img_path):
            card = QWidget()
            card.setFixedSize(270, 350)
            card.setObjectName("ExerciseCard")

            # Clean Translucent Base Layout Stylesheet
            card.setStyleSheet("""
                QWidget#ExerciseCard {
                    background-color: rgba(30, 41, 59, 210);
                    border-radius: 18px;
                    border: 1px solid rgba(255, 255, 255, 15);
                }
                QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(20, 20, 20, 20)

            img = QLabel()
            pixmap = QPixmap(os.path.join(base_dir, img_path))
            img.setPixmap(pixmap.scaled(
                180, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            img.setAlignment(Qt.AlignmentFlag.AlignCenter)

            title_lbl = QLabel(title)
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_lbl.setStyleSheet("font-size:18px; font-weight:bold; color:white;")

            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_lbl.setStyleSheet("font-size:12px; color:#cbd5e1;")

            btn = QPushButton("Start")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedWidth(140)
            btn.setStyleSheet("""
                QPushButton {
                    background-color:#38bdf8;
                    color:black;
                    padding:8px;
                    border-radius:10px;
                    font-weight:bold;
                }
                QPushButton:hover {
                    background-color:#0ea5e9;
                }
            """)

            layout.addWidget(img)
            layout.addSpacing(10)
            layout.addWidget(title_lbl)
            layout.addSpacing(5)
            layout.addWidget(desc_lbl)
            layout.addStretch()
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            card.setLayout(layout)

            # ------------------------------------------------======
            # 🔥 HOVER ANIMATION LOGIC (FIXED: RELATIVE POS ENGINE)
            # ------------------------------------------------======
            card.anim = QPropertyAnimation(card, b"pos")
            card.anim.setDuration(150)  # Snappy and sleek transition
            card.original_pos = None     # Will be captured dynamically

            def enterEvent(event):
                # Hover Par Card ko Glow aur Neon Border do
                card.setStyleSheet("""
                    QWidget#ExerciseCard {
                        background-color: rgba(56, 189, 248, 40);
                        border: 2px solid #38bdf8;
                        border-radius: 18px;
                    }
                    QLabel { background: transparent; }
                """)
                
                # Agar original position store nahi hui ya resize hua tha, to lock karein
                if card.original_pos is None:
                    card.original_pos = card.pos()
                
                card.anim.stop()
                card.anim.setStartValue(card.pos())
                # Hamesha original baseline se 15 pixels lift karega (No drifting down!)
                card.anim.setEndValue(QPoint(card.original_pos.x(), card.original_pos.y() - 15))
                card.anim.start()
                QWidget.enterEvent(card, event)

            def leaveEvent(event):
                # Hover Khatam hone par reset to original dark layout
                card.setStyleSheet("""
                    QWidget#ExerciseCard {
                        background-color: rgba(30, 41, 59, 210);
                        border-radius: 18px;
                        border: 1px solid rgba(255, 255, 255, 15);
                    }
                    QLabel { background: transparent; }
                """)
                
                card.anim.stop()
                card.anim.setStartValue(card.pos())
                # Hamesha exact absolute origin point par wapas layega
                if card.original_pos is not None:
                    card.anim.setEndValue(card.original_pos)
                card.anim.start()
                QWidget.leaveEvent(card, event)

            card.enterEvent = enterEvent
            card.leaveEvent = leaveEvent

            return card, btn
        
        # ======================================================
        # CARDS INITIALIZATION
        # ======================================================
        self.card1, self.btn1 = create_card(
            "Biceps Curls",
            "Build arm strength and improve definition.",
            "assets/biceps.png"
        )

        self.card2, self.btn2 = create_card(
            "Squats",
            "Strengthen legs and improve stability.",
            "assets/squats.png"
        )

        self.card3, self.btn3 = create_card(
            "Crunches",
            "Core exercise for abs strength.",
            "assets/crunches.png"
        )

        self.btn1.clicked.connect(self.open_biceps)
        self.btn2.clicked.connect(self.open_squats)
        self.btn3.clicked.connect(self.open_crunches)

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.setSpacing(40)

        row.addWidget(self.card1)
        row.addWidget(self.card2)
        row.addWidget(self.card3)

        wrapper = QVBoxLayout()
        wrapper.addStretch()
        wrapper.addLayout(row)
        wrapper.addStretch()

        # ======================================================
        # BACK BUTTON
        # ======================================================
        self.back_btn = QPushButton("⬅ Back")
        self.back_btn.setFixedSize(200, 45)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.go_back)

        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color:#334155;
                color:white;
                border-radius:10px;
                font-weight:bold;
            }
            QPushButton:hover {
                background-color:#475569;
            }
        """)

        # ======================================================
        # MAIN LAYOUT
        # ======================================================
        main = QVBoxLayout()
        main.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main.addWidget(self.header)
        main.addWidget(self.sub)
        main.addSpacing(20)
        main.addLayout(wrapper)
        main.addSpacing(20)
        main.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main)

    def update_background(self):
        h, w, ch = self.bg_raw.shape
        qt_img = QImage(self.bg_raw.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.bg.setPixmap(
            QPixmap.fromImage(qt_img).scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation  # ⚡ OPTIMIZED: Render lag khatam karne k liye
            )
        )

    def resizeEvent(self, event):
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.update_background()
        
        # Window resize hone par cards ki absolute cache coordinates clear karein taake repositioning glitch na ho
        for card in [self.card1, self.card2, self.card3]:
            card.original_pos = None
            
        super().resizeEvent(event)

    # ======================================================
    # NAVIGATION WITH LOADING DIALOG
    # ======================================================
    def apply_screen_blur(self):
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(15)
        self.setGraphicsEffect(blur_effect)

    def remove_screen_blur(self):
        self.setGraphicsEffect(None)

    def open_biceps(self):
        self.apply_screen_blur()
        dialog = LoadingDialog("Biceps Curl", self)
        self.biceps = BicepsScreen(self)
        dialog.exec()
        self.remove_screen_blur()
        self.biceps.showMaximized()
        self.hide()

    def open_squats(self):
        self.apply_screen_blur()
        dialog = LoadingDialog("Squats", self)
        self.squats = SquatsScreen(self)
        dialog.exec()
        self.remove_screen_blur()
        self.squats.showMaximized()
        self.hide()

    def open_crunches(self):
        self.apply_screen_blur()
        dialog = LoadingDialog("Crunches", self)
        self.crunches = CrunchesScreen(self)
        dialog.exec()
        self.remove_screen_blur()
        self.crunches.showMaximized()
        self.hide()

    def go_back(self):
        if self.previous_screen:
            self.previous_screen.show()
        self.close()