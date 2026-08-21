from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QTime
from PyQt6.QtGui import QPixmap, QImage
import cv2, os, numpy as np
from utils.camera_manager import CameraManager
from ui.loading_dialog import LoadingDialog
from ui.summary_dialog import WorkoutSummaryDialog
from core.pose_detector import PoseDetector
from core.exercises.crunch_analyzer import CrunchAnalyzer
from core.drawing_utils import draw_landmarks


# Background Camera Thread for Workout Screens
class CrunchesCameraThread(QThread):
    camera_instantiated = pyqtSignal(object)

    def run(self):
        # Direct global manager se preloaded active camera instance uthaye ga
        cap = CameraManager.get_camera()
        self.camera_instantiated.emit(cap)


class CrunchesScreen(QWidget):
    def __init__(self, previous_screen = None):
        super().__init__()
        self.previous_screen = previous_screen
        self.cap = None
        self.camera_ready = False

        # 🔥 PYQT6 COMPATIBLE MEDIAPIPE TIMECODE INITIALIZER
        self.frame_timer = QTime.currentTime()

        # 🔥 AI ENGINES INITIALIZATION
        self.pose_detector = PoseDetector()
        self.crunch_analyzer = CrunchAnalyzer()

        # ---------------- WINDOW ----------------
        self.setWindowTitle("Crunches Workout")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        base_dir = os.path.dirname(os.path.dirname(__file__))

        # ======================================================
        # BACKGROUND SETUP
        # ======================================================
        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())

        bg_path = os.path.join(base_dir, "assets", "background.jpg")
        
        if not os.path.exists(bg_path):
            bg_img = np.zeros((700, 1000, 3), dtype=np.uint8)
        else:
            bg_img = cv2.imread(bg_path)
            bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB)
            bg_img = cv2.GaussianBlur(bg_img, (25, 25), 0)

        self.bg_raw = bg_img  
        self.update_background()
        self.bg.lower()
    
        # ======================================================
        # HEADER
        # ======================================================
        self.header = QLabel("🧘 Crunches Workout - AI Trainer")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setObjectName("header")

        # ======================================================
        # CAMERA LABEL WIDGET
        # ======================================================
        self.camera = QLabel()
        self.camera.setMinimumSize(420, 360)
        self.camera.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera.setStyleSheet("""
            background-color:#020617;
            border-radius:35px;
            border:2px solid #1e293b;
        """)

        # ======================================================
        # REDESIGNED TABS (Matching Friend's Crunch Metrics)
        # ======================================================
        def create_card(title):
            card = QLabel(title + ": --")
            card.setStyleSheet("""
                font-size:15px;
                padding:16px;
                background-color:#1e293b;
                border-radius:14px;
                color:white;
            """)
            return card
        
        # Dost ke exact crunch parameters map kar diye tabs par:
        self.reps_card = create_card("Reps Count")
        self.stage_card = create_card("Stage State")
        self.torso_angle_card = create_card("Torso Angle")
        self.knee_angle_card = create_card("Avg Knee Angle")

        self.audio_box = QLabel("🎧 AI Feedback: Lay down sideways to start crunches...")
        self.audio_box.setWordWrap(True)
        self.audio_box.setStyleSheet("""
            font-size:14px;
            padding:16px;
            background-color:#1e293b;
            border-radius:12px;
            color:#38bdf8;
        """)
        
        # ======================================================
        # BUTTONS
        # ======================================================
        self.restart_btn = QPushButton("Restart")
        self.finish_btn = QPushButton("Finish Workout")
        self.back_btn = QPushButton("⬅ Back")

        self.back_btn.clicked.connect(self.go_back)
        self.restart_btn.clicked.connect(self.reset_workout_stats)
        self.finish_btn.clicked.connect(self.show_workout_summary)

        for btn in [self.restart_btn, self.finish_btn, self.back_btn]:
            btn.setFixedHeight(40)
            btn.setFixedWidth(250)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # ======================================================
        # ASSEMBLING THE UI STRUCTURE
        # ======================================================
        right = QVBoxLayout()
        right.setSpacing(12)

        right.addWidget(self.reps_card)
        right.addWidget(self.stage_card)
        right.addWidget(self.torso_angle_card)
        right.addWidget(self.knee_angle_card)

        right.addSpacing(20)
        right.addWidget(self.audio_box)
        right.addSpacing(20)
        
        right.addWidget(self.finish_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        right.addWidget(self.restart_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        right.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        right.addStretch()

        body = QHBoxLayout()
        body.setSpacing(20)
        body.addWidget(self.camera, stretch=3)
        body.addLayout(right, stretch=2)

        main = QVBoxLayout()
        main.addWidget(self.header)
        main.addSpacing(10)
        main.addLayout(body)
        self.setLayout(main)

        self.setStyleSheet("""
            QLabel#header {
                font-size:20px; font-weight:bold; padding:12px; color:white;
                background-color:rgba(30, 41, 59, 200); border-radius:12px;
            }
            QPushButton {
                background-color:#38bdf8; color:white; border-radius:10px; font-weight:bold;
            }
            QPushButton:hover { background-color:#0ea5e9; }
        """)

        # Thread call safely loading pre-warmed up global camera cache pointer
        self.cam_thread = CrunchesCameraThread()
        self.cam_thread.camera_instantiated.connect(self.on_camera_initialized)
        self.cam_thread.start()

    def on_camera_initialized(self, cap_object):
        self.cap = cap_object
        self.camera_ready = True
        if self.isVisible():
            self.start_video_stream()

    def start_video_stream(self):
        if not hasattr(self, "timer"):
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(33) # Dynamic 30 FPS timing capture rate

    def showEvent(self, event):
        super().showEvent(event)
        if self.camera_ready:
            self.start_video_stream()

    def update_background(self):
        h, w, ch = self.bg_raw.shape
        qt_img = QImage(self.bg_raw.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.bg.setPixmap(QPixmap.fromImage(qt_img).scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))

    def resizeEvent(self, event):
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.update_background()
        super().resizeEvent(event)

    # ======================================================
    # 🔥 LIVE CRUNCH PROCESSING SYSTEM LOOP
    # ======================================================
    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            # Mirror effect flip orientation for easier screen targeting view
            frame = cv2.flip(frame, 1)
            
            # Dynamic increasing unique milliseconds time tracker calculation
            timestamp_ms = self.frame_timer.msecsTo(QTime.currentTime())

            try:
                # 1. Fire frame landmarks location using your friend's detector logic
                result = self.pose_detector.detect(frame, timestamp_ms)

                if result.pose_landmarks:
                    landmarks = result.pose_landmarks[0]

                    # 2. Extract calculations utilizing CrunchAnalyzer
                    data = self.crunch_analyzer.process(landmarks)

                    # 3. Asynchronously trigger non-blocking speech playback 
                    self.crunch_analyzer.audio_feedback()

                    # 4. Generate visual graphs links lines drawing directly onto array 
                    draw_landmarks(frame, landmarks)

                    # 5. Populate display data maps matching exactly onto tabs text elements
                    self.reps_card.setText(f"Reps Count: {data['counter']}")
                    self.stage_card.setText(f"Stage State: {data['stage'].upper()}")
                    self.torso_angle_card.setText(f"Torso Angle: {int(data['torso'])}°")
                    self.knee_angle_card.setText(f"Avg Knee Angle: {int(data['avg_knee'])}°")
                    
                    if hasattr(self.crunch_analyzer, 'feedback') and self.crunch_analyzer.feedback:
                        self.audio_box.setText(f"🎧 AI Feedback: {self.crunch_analyzer.feedback}")

            except Exception as e:
                # Intercept logic exceptions to avoid GUI execution pipeline crash freezes
                print(f"Exception encountered within live frame extraction tracker: {e}")

            # Safe standard PyQt frame pixel layout representation conversion mapping
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w

            img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera.setPixmap(QPixmap.fromImage(img).scaled(
                self.camera.width(), self.camera.height(),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))

    def reset_workout_stats(self):
        # Directly target and clear your friend's logic properties tracking state values
        if hasattr(self.crunch_analyzer, 'counter'):
            self.crunch_analyzer.counter = 0
            self.crunch_analyzer.stage = "down"
            self.crunch_analyzer.feedback = "None"
            self.audio_box.setText("🎧 AI Feedback: Crunches stats successfully reset!")

    def show_workout_summary(self):
        # 1. Freeze camera frame parsing timer loop
        if hasattr(self, "timer"):
            self.timer.stop()

        stats = {
            "Total Crunches Count": getattr(self.crunch_analyzer, 'counter', 0),
            "raw_feedback": getattr(self.crunch_analyzer, 'feedback', 'None')
        }

        # 2. Fire custom layout preparation 2 seconds alert loader popup
        prep_dialog = LoadingDialog(
            "Crunches Workout", 
            self, 
            status1="Preparing Workout Summary...", 
            status2="Compiling performance analytics...", 
            duration=2000
        )
        prep_dialog.exec()

        # 3. Cleanup core active instances
        self.cap = None 
        self.camera_ready = False
        
        if self.previous_screen:
            # 4. Select exercise window show aur blur karo
            self.previous_screen.showMaximized()
            self.previous_screen.apply_screen_blur()

            # 5. Open Frameless summary window
            dialog = WorkoutSummaryDialog("Crunches Workout", stats, self.previous_screen)
            dialog.exec()
            
            # 6. Cleanup blur
            self.previous_screen.remove_screen_blur()
            
        self.close()

    def go_back(self):
        if hasattr(self, "timer"):
            self.timer.stop()
        self.cap = None 
        self.camera_ready = False
        self.previous_screen.showMaximized()
        self.close()

    def closeEvent(self, event):
        if hasattr(self, "timer"):
            self.timer.stop()
        event.accept()