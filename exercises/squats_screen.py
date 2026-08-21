from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QTime
from PyQt6.QtGui import QPixmap, QImage
import cv2, os, numpy as np
from ui.loading_dialog import LoadingDialog
from ui.summary_dialog import WorkoutSummaryDialog
from utils.camera_manager import CameraManager
from core.pose_detector import PoseDetector
from core.exercises.squat_analyzer import SquatAnalyzer
from core.drawing_utils import draw_landmarks


# Background Camera Thread for Workout Screens
class SquatsCameraThread(QThread):
    camera_instantiated = pyqtSignal(object)

    def run(self):
        # Direct global manager se ready camera layega without any delay
        cap = CameraManager.get_camera()
        self.camera_instantiated.emit(cap)


class SquatsScreen(QWidget):
    def __init__(self, previous_screen = None):
        super().__init__()
        self.previous_screen = previous_screen
        self.cap = None
        self.camera_ready = False

        # 🔥 PYQT6 COMPATIBLE TIMECODE INITIALIZER FOR MEDIAPIPE VIDEO MODE
        self.frame_timer = QTime.currentTime()

        # 🔥 AI ENGINES INITIALIZATION
        self.pose_detector = PoseDetector()
        self.squat_analyzer = SquatAnalyzer()

        # ---------------- WINDOW ----------------
        self.setWindowTitle("Squats Workout")
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
        self.header = QLabel("🏋️ Squats Workout - AI Trainer")
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
        # REDESIGNED TABS (Matching Friend's Squat Output Data)
        # ======================================================
        def create_card(title):
            card = QLabel(title + ": --")
            card.setStyleSheet("""
                font-size:14px;
                padding:12px;
                background-color:#1e293b;
                border-radius:12px;
                color:white;
            """)
            return card
        
        # Dost ke exact squat parameters ke mutabiq panel cards redesign:
        self.reps_card = create_card("Reps Count")
        self.stage_card = create_card("Stage State")
        self.left_angle_card = create_card("Left Knee Angle")
        self.right_angle_card = create_card("Right Knee Angle")
        self.avg_angle_card = create_card("Average Angle")
        self.symmetry_card = create_card("Symmetry Diff")
        self.hip_drop_card = create_card("Hip Drop")

        self.audio_box = QLabel("🎧 AI Feedback: Stand straight in camera frame to start squats...")
        self.audio_box.setWordWrap(True)
        self.audio_box.setStyleSheet("""
            font-size:14px;
            padding:14px;
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
            btn.setFixedHeight(38)
            btn.setFixedWidth(240)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # ======================================================
        # LAYOUT ASSEMBLY
        # ======================================================
        right = QVBoxLayout()
        right.setSpacing(8)

        right.addWidget(self.reps_card)
        right.addWidget(self.stage_card)
        right.addWidget(self.left_angle_card)
        right.addWidget(self.right_angle_card)
        right.addWidget(self.avg_angle_card)
        right.addWidget(self.symmetry_card)
        right.addWidget(self.hip_drop_card)

        right.addSpacing(5)
        right.addWidget(self.audio_box)
        right.addSpacing(5)
        
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

        # Hardware Camera Preload connection thread activation
        self.cam_thread = SquatsCameraThread()
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
            self.timer.start(33) # Dynamic stable ~30 FPS feed rendering rate

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


    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            # Mirror effect flip orientation
            frame = cv2.flip(frame, 1)
            
            # Dynamic increasing milliseconds calculation for MediaPipe Video Mode
            timestamp_ms = self.frame_timer.msecsTo(QTime.currentTime())

            try:
                # 1. Detect Frame Landmarks using friend's engine structure
                result = self.pose_detector.detect(frame, timestamp_ms)

                if result.pose_landmarks:
                    landmarks = result.pose_landmarks[0]

                    # 2. Extract workout metrics via SquatAnalyzer processing logic
                    data = self.squat_analyzer.process(landmarks)

                    # 3. Fire asynchronous non-blocking audio feedback call
                    self.squat_analyzer.audio_feedback()

                    # 4. Draw skeletal visualization links overlay lines onto frame matrix
                    draw_landmarks(frame, landmarks)

                    # 5. Refresh display cards dynamically mapping friend's exact output fields
                    self.reps_card.setText(f"Reps Count: {data['counter']}")
                    self.stage_card.setText(f"Stage State: {data['stage'].upper()}")
                    self.left_angle_card.setText(f"Left Knee Angle: {int(data['left_angle'])}°")
                    self.right_angle_card.setText(f"Right Knee Angle: {int(data['right_angle'])}°")
                    self.avg_angle_card.setText(f"Average Angle: {int(data['avg_angle'])}°")
                    self.symmetry_card.setText(f"Symmetry Diff: {int(data['symmetry'])}°")
                    self.hip_drop_card.setText(f"Hip Drop: {data['hip_drop']:.2f}")
                    
                    if hasattr(self.squat_analyzer, 'feedback') and self.squat_analyzer.feedback:
                        self.audio_box.setText(f"🎧 AI Feedback: {self.squat_analyzer.feedback}")

            except Exception as e:
                # Intercept logic loop calculations exceptions to prevent PyQt pipeline freeze crash
                print(f"Exception encountered inside live squat pipeline: {e}")

            # Safe standard PyQt format pixel conversion setup
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w

            img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera.setPixmap(QPixmap.fromImage(img).scaled(
                self.camera.width(), self.camera.height(),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))

    def reset_workout_stats(self):
        # Directly reset tracking attributes inside friend's class instance
        if hasattr(self.squat_analyzer, 'counter'):
            self.squat_analyzer.counter = 0
            self.squat_analyzer.stage = "up"
            self.squat_analyzer.initial_hip_y = None
            self.squat_analyzer.feedback = "None"
            self.audio_box.setText("🎧 AI Feedback: Squats performance stats successfully reset!")

    def show_workout_summary(self):
        # 1. Stop video matrix updater timer immediately
        if hasattr(self, "timer"):
            self.timer.stop()

        stats = {
            "Total Squats Count": getattr(self.squat_analyzer, 'counter', 0),
            "Max Symmetry Offset": f"{int(abs(getattr(self.squat_analyzer, 'left_angle', 180) - getattr(self.squat_analyzer, 'right_angle', 180)))}°",
            "Final Hip Drop Value": f"{getattr(self.squat_analyzer, 'hip_drop', 0.0):.2f}",
            "raw_feedback": getattr(self.squat_analyzer, 'feedback', 'Standing')
        }

        # 2. Trigger dynamic loader for 2000 milliseconds
        prep_dialog = LoadingDialog(
            "Squats Workout", 
            self, 
            status1="Preparing Workout Summary...", 
            status2="Calculating balance and hip symmetry...", 
            duration=2000
        )
        prep_dialog.exec()

        self.cap = None 
        self.camera_ready = False
        
        if self.previous_screen:
            # 3. Unhide parent layout window screen and toggle blur graphic effect
            self.previous_screen.showMaximized()
            self.previous_screen.apply_screen_blur()

            # 4. Render clean overview data pop-up modal
            dialog = WorkoutSummaryDialog("Squats Workout", stats, self.previous_screen)
            dialog.exec()
            
            # 5. Drop layout transparency blur overlay filter
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