import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect


class WorkoutSummaryDialog(QDialog):

    def __init__(self, exercise_name, stats_data, parent=None):
        super().__init__(parent)
        self.exercise_name = exercise_name
        self.stats_data = stats_data

        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # 🔥 1.5x UPSCALED DIMENSIONS (Width: 630, Height: 720)
        self.setFixedWidth(630)
        self.setMinimumHeight(720)

        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 630, 720)
        self.container.setStyleSheet(
            """
            QWidget {
                background-color: #0f172a;
                border: 2px solid #38bdf8;
                border-radius: 24px;
            }
            QLabel {
                color: white;
                font-size: 16px;
                border: none;
                background: transparent;
            }
            QLabel#title {
                font-size: 32px;
                font-weight: bold;
                color: #38bdf8;
                padding-bottom: 8px;
            }
            QLabel#efficiency_lbl {
                font-size: 42px;
                font-weight: bold;
                color: #22c55e;
                margin-top: 5px;
            }
            QLabel#feedback_lbl {
                font-size: 16px;
                font-style: italic;
                color: #e2e8f0;
                background-color: #1e293b;
                padding: 18px;
                border-radius: 12px;
                border-left: 5px solid #38bdf8;
                line-height: 24px;
            }
            QPushButton {
                background-color: #38bdf8;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #0ea5e9;
            }
            QPushButton#close_btn {
                background-color: #475569;
            }
            QPushButton#close_btn:hover {
                background-color: #334155;
            }
            QLabel#status_label {
                color: #38bdf8;
                font-weight: bold;
                font-size: 14px;
            }
        """
        )

        layout = QVBoxLayout(self.container)
        layout.setSpacing(22)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(f"🎉 {self.exercise_name}", self.container)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("AI Personal Trainer Session Summary", self.container)
        sub.setStyleSheet("color: #94a3b8; font-size: 14px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        eff_title = QLabel("Workout Efficiency", self.container)
        eff_title.setStyleSheet("color: #94a3b8; font-size: 15px; text-transform: uppercase; font-weight: 600;")
        eff_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(eff_title)

        efficiency, ai_feedback_text = self.calculate_metrics()

        self.eff_val = QLabel(f"{efficiency}%", self.container)
        self.eff_val.setObjectName("efficiency_lbl")
        self.eff_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.eff_val)

        stats_box = QVBoxLayout()
        stats_box.setSpacing(10)
        for key, value in self.stats_data.items():
            if "raw" not in key.lower():
                item_lbl = QLabel(f"<b>{key}:</b> {value}", self.container)
                item_lbl.setStyleSheet("font-size: 17px; color: #f1f5f9;")
                stats_box.addWidget(item_lbl)
        layout.addLayout(stats_box)

        coach_title = QLabel("📢 AI Coach Evaluation:", self.container)
        coach_title.setStyleSheet("font-weight: bold; color: #94a3b8; font-size: 16px;")
        layout.addWidget(coach_title)

        self.feedback_box = QLabel(ai_feedback_text, self.container)
        self.feedback_box.setObjectName("feedback_lbl")
        self.feedback_box.setWordWrap(True)
        layout.addWidget(self.feedback_box)

        self.status_msg = QLabel("", self.container)
        self.status_msg.setObjectName("status_label")
        self.status_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_msg)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(18)

        self.save_btn = QPushButton("💾 Save Log", self.container)
        self.back_btn = QPushButton("⬅ Close Menu", self.container)
        self.back_btn.setObjectName("close_btn")

        self.save_btn.clicked.connect(lambda: self.save_summary_to_file(efficiency, ai_feedback_text))
        self.back_btn.clicked.connect(self.start_pop_out)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.back_btn)
        layout.addLayout(btn_layout)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

    def showEvent(self, event):
        """🔥 Fixed: Pure Vertical Slide Up Pop-In for Summary Box"""
        super().showEvent(event)
        
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(320)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()

        orig_geo = self.geometry()
        self.scale_anim = QPropertyAnimation(self, b"geometry")
        self.scale_anim.setDuration(320)
        # Niche se slide up hote hue height open hogi
        self.scale_anim.setStartValue(QRect(orig_geo.x(), orig_geo.y() + 120, orig_geo.width(), 0))
        self.scale_anim.setEndValue(orig_geo)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.scale_anim.start()

    def start_pop_out(self):
        """🔥 Fixed: Pure Vertical Slide Down Pop-Out for Summary Box"""
        self.out_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.out_fade.setDuration(260)
        self.out_fade.setStartValue(1.0)
        self.out_fade.setEndValue(0.0)
        
        orig_geo = self.geometry()
        self.out_scale = QPropertyAnimation(self, b"geometry")
        self.out_scale.setDuration(260)
        self.out_scale.setStartValue(orig_geo)
        # Niche slip hotay hue compress ho jaye ga
        self.out_scale.setEndValue(QRect(orig_geo.x(), orig_geo.y() + 120, orig_geo.width(), 0))
        self.out_scale.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.out_fade.finished.connect(self.accept)
        
        self.out_fade.start()
        self.out_scale.start()

    def calculate_metrics(self):
        reps = 0
        if "Total Squats Count" in self.stats_data:
            reps = self.stats_data["Total Squats Count"]
        elif "Total Crunches Count" in self.stats_data:
            reps = self.stats_data["Total Crunches Count"]
        else:
            reps = self.stats_data.get("Left Reps Counter", 0) + self.stats_data.get("Right Reps Counter", 0)

        feedback_str = str(self.stats_data.get("raw_feedback", "")).lower()

        if reps == 0:
            efficiency = 0
            feedback_text = "Poor Workout: Workout session recorded no repetitions. Position your body fully inside the camera frame and follow the range of motion instructions to start counting."
        elif any(x in feedback_str for x in ["balance", "drop", "slowly", "contract", "back"]):
            efficiency = 75
            feedback_text = "Good Workout: Great physical exertion observed! However, your dynamic alignment was slightly compromised during some reps. Focus on perfect balance and execution speed next time."
        else:
            efficiency = 95
            feedback_text = "Best Workout: Flawless posture execution tracked by AI! Your full range of motion, stable symmetry, and balanced kinetic movement were exceptional. Keep up the amazing work!"

        return efficiency, feedback_text

    def save_summary_to_file(self, efficiency, feedback_text):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filename = f"{self.exercise_name.lower().replace(' ', '_')}_summary.txt"
            file_path = os.path.join(base_dir, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=========================================\n")
                f.write(f"        AI PERSONAL TRAINER REPORT       \n")
                f.write("=========================================\n\n")
                f.write(f" Exercise Name      : {self.exercise_name}\n")
                f.write(f" Session Efficiency : {efficiency}%\n")
                f.write("-----------------------------------------\n")
                f.write(" PERFORMANCE METRICS:\n")
                for key, value in self.stats_data.items():
                    if "raw" not in key.lower():
                        f.write(f"  - {key:<18}: {value}\n")
                f.write("-----------------------------------------\n")
                f.write(" AI COACH EVALUATION:\n")
                f.write(f" {feedback_text}\n")
                f.write("=========================================\n")

            self.status_msg.setText(f"✔ File logged at root/{filename}")
            self.save_btn.setEnabled(False)
        except Exception as e:
            self.status_msg.setStyleSheet("color: #ef4444;")
            self.status_msg.setText(f"❌ Error: {str(e)}")