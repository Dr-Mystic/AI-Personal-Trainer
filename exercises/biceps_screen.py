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
from core.exercises.bicep_curl_analyzer import BicepCurlAnalyzer
from core.drawing_utils import draw_landmarks


# Background Camera Thread for Workout Screens
class BicepsCameraThread(QThread):
    camera_instantiated = pyqtSignal(object)

    def run(self):
        cap = CameraManager.get_camera()
        self.camera_instantiated.emit(cap)


class BicepsScreen(QWidget):
    def __init__(self, previous_screen = None):
        super().__init__()
        self.previous_screen = previous_screen
        self.cap = None
        self.camera_ready = False

        # 🔥 FIXED MEDIAPIPE TIMECODE TRACKER FOR PYQT6
        self.frame_timer = QTime.currentTime()

        # 🔥 BACKEND LOGIC OBJECTS INITIALIZATION
        self.pose_detector = PoseDetector()
        self.bicep_analyzer = BicepCurlAnalyzer()

        # ---------------- WINDOW ----------------
        self.setWindowTitle("Biceps Workout")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        base_dir = os.path.dirname(os.path.dirname(__file__))

        # ======================================================
        # BACKGROUND (FIXED)
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
        self.header = QLabel("💪 Biceps Workout - AI Trainer")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setObjectName("header")

        # ======================================================
        # CAMERA LABEL PLACEHOLDER
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
        # DYNAMIC MODIFIED RESULTS TABS (Matching Friend's Data Output)
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
        
        self.left_reps_card = create_card("Left Reps")
        self.right_reps_card = create_card("Right Reps")
        self.left_stage_card = create_card("Left Stage")
        self.right_stage_card = create_card("Right Stage")
        self.left_angle_card = create_card("Left Angle")
        self.right_angle_card = create_card("Right Angle")

        self.audio_box = QLabel("🎧 AI Feedback: Waiting for curl movement...")
        self.audio_box.setWordWrap(True)
        self.audio_box.setStyleSheet("""
            font-size:14px;
            padding:16px;
            background-color:#1e293b;
            border-radius:12px;
            color:#38bdf8;
        """)
        
        # ======================================================
        # BUTTONS CREATION
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
        # LAYOUT ASSEMBLY
        # ======================================================
        right = QVBoxLayout()
        right.setSpacing(10)

        right.addWidget(self.left_reps_card)
        right.addWidget(self.right_reps_card)
        right.addWidget(self.left_stage_card)
        right.addWidget(self.right_stage_card)
        right.addWidget(self.left_angle_card)
        right.addWidget(self.right_angle_card)

        right.addSpacing(10)
        right.addWidget(self.audio_box)
        right.addSpacing(10)
        
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

        self.cam_thread = BicepsCameraThread()
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
            self.timer.start(33)

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
    # 🔥 LIVE FRAME PROCESSING PIPELINE WITH AI OVERLAY
    # ======================================================
    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            # 🔥 FIXED: PyQt6 compatible timestamp calculator for MediaPipe Video Mode
            timestamp_ms = self.frame_timer.msecsTo(QTime.currentTime())

            try:
                # 1. Detect Landmarks via friend's engine
                result = self.pose_detector.detect(frame, timestamp_ms)

                if result.pose_landmarks:
                    landmarks = result.pose_landmarks[0]

                    # 2. Feed landmarks to his Bicep Curl business rules engine
                    data = self.bicep_analyzer.process(landmarks)

                    # 3. Handle threading-safe audio feedback execution asynchronously
                    self.bicep_analyzer.audio_feedback()

                    # 4. Draw overlay skeletal system graph links directly onto current video matrix
                    draw_landmarks(frame, landmarks)

                    # 5. Refresh UI display components dynamically mapping friend's exact naming fields
                    self.left_reps_card.setText(f"Left Reps: {data['right_counter']}")
                    self.right_reps_card.setText(f"Right Reps: {data['left_counter']}")
                    self.left_stage_card.setText(f"Left Stage: {data['right_stage'].upper()}")
                    self.right_stage_card.setText(f"Right Stage: {data['left_stage'].upper()}")
                    self.left_angle_card.setText(f"Left Angle: {int(data['right_angle'])}°")
                    self.right_angle_card.setText(f"Right Angle: {int(data['left_angle'])}°")
                    
                    if hasattr(self.bicep_analyzer, 'feedback') and self.bicep_analyzer.feedback:
                        self.audio_box.setText(f"🎧 AI Feedback: {self.bicep_analyzer.feedback}")

            except Exception as e:
                print(f"Frame analysis pipeline exception bypassed: {e}")

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w

            img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera.setPixmap(QPixmap.fromImage(img).scaled(
                self.camera.width(), self.camera.height(),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))

    def reset_workout_stats(self):
        if hasattr(self.bicep_analyzer, 'left_counter'):
            self.bicep_analyzer.left_counter = 0
            self.bicep_analyzer.right_counter = 0
            self.bicep_analyzer.left_stage = "down"
            self.bicep_analyzer.right_stage = "down"
            self.bicep_analyzer.feedback = "None"
            self.audio_box.setText("🎧 AI Feedback: Counter reset successful. Ready!")
    
    def show_workout_summary(self):
        # 1. Sab se pehle live camera video thread processing freeze kar do
        if hasattr(self, "timer"):
            self.timer.stop()

        # 2. Extract stats from analysis engine variables
        stats = {
            "Left Reps Counter": getattr(self.bicep_analyzer, 'right_counter', 0),
            "Right Reps Counter": getattr(self.bicep_analyzer, 'left_counter', 0),
            "raw_feedback": getattr(self.bicep_analyzer, 'feedback', 'None')
        }

        # 3. Open your customized loading dialog for exactly 2 seconds
        prep_dialog = LoadingDialog(
            "Biceps Workout", 
            self, 
            status1="Preparing Workout Summary...", 
            status2="Processing skeletal data metrics...", 
            duration=2000
        )
        prep_dialog.exec()

        # 4. Background workout screen close karo aur parent menu screen wapas layo
        self.cap = None 
        self.camera_ready = False
        
        if self.previous_screen:
            # 5. Main selection menu ko wapas show karo aur temporarily blur apply karo
            self.previous_screen.showMaximized()
            self.previous_screen.apply_screen_blur()

            # 6. Smooth modern summary popup show karo
            dialog = WorkoutSummaryDialog("Biceps Curl Workout", stats, self.previous_screen)
            dialog.exec()
            
            # 7. Close dabane ke baad blur effect clean remove kar do
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