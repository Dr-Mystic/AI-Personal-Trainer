import cv2
import mediapipe as mp
import numpy as np

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# =========================================================
# ANGLE CALCULATION
# =========================================================

def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc)
    )

    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    angle = np.degrees(np.arccos(cosine_angle))

    return angle


# =========================================================
# MEDIAPIPE TASKS SETUP
# =========================================================

base_options = python.BaseOptions(
    model_asset_path="pose_landmarker_heavy.task"
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1
)

detector = vision.PoseLandmarker.create_from_options(options)

# =========================================================
# REP COUNT VARIABLES
# =========================================================

counter = 0
stage = "up"

# Used for baseline standing posture
initial_hip_y = None

# =========================================================
# WEBCAM SETUP
# =========================================================

cap = cv2.VideoCapture(0)

# Reduce lag
cap.set(3, 1920)
cap.set(4, 1080)

timestamp = 0

# =========================================================
# MAIN LOOP
# =========================================================

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert to MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Pose Detection
    result = detector.detect_for_video(
        mp_image,
        timestamp
    )

    h, w, _ = frame.shape
    feedback = "None"

    # =====================================================
    # IF POSE DETECTED
    # =====================================================

    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        # =================================================
        # IMPORTANT LANDMARKS
        # =================================================

        hip = landmarks[23]      # LEFT HIP
        knee = landmarks[25]     # LEFT KNEE
        ankle = landmarks[27]    # LEFT ANKLE

        shoulder = landmarks[11] # LEFT SHOULDER

        # =================================================
        # STORE INITIAL STANDING HIP POSITION
        # =================================================

        if initial_hip_y is None:
            initial_hip_y = hip.y

        # =================================================
        # POINTS
        # =================================================

        hip_point = (hip.x, hip.y)
        knee_point = (knee.x, knee.y)
        ankle_point = (ankle.x, ankle.y)

        # =================================================
        # CALCULATE KNEE ANGLE
        # =================================================

        angle = calculate_angle(
            hip_point,
            knee_point,
            ankle_point
        )

        # =================================================
        # HIP DROP CALCULATION
        # =================================================

        hip_drop = hip.y - initial_hip_y

        # =================================================
        # IMPROVED SQUAT DETECTION LOGIC
        # =================================================

        # Going down into squat
        if angle < 100 and hip_drop > 0.18:
            feedback = "Lower Your Hips"

        if angle < 70 and hip_drop > 0.28:
            stage = "down"
            feedback = "Good Form"

        # Returning back up
        if angle > 160 and hip_drop < 0.05 and stage == "down":
            stage = "up"
            counter += 1
            feedback = "Go Lower"

        # =================================================
        # DRAW LANDMARKS
        # =================================================

        for landmark in landmarks:

            cx = int(landmark.x * w)
            cy = int(landmark.y * h)

            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # =================================================
        # DRAW SKELETON CONNECTIONS
        # =================================================

        connections = [

            # Arms
            (11, 13), (13, 15),
            (12, 14), (14, 16),

            # Shoulders
            (11, 12),

            # Torso
            (11, 23), (12, 24),
            (23, 24),

            # Legs
            (23, 25), (25, 27),
            (24, 26), (26, 28)
        ]

        for start_idx, end_idx in connections:

            start = landmarks[start_idx]
            end = landmarks[end_idx]

            x1 = int(start.x * w)
            y1 = int(start.y * h)

            x2 = int(end.x * w)
            y2 = int(end.y * h)

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

        # =================================================
        # DISPLAY ANGLE
        # =================================================

        knee_x = int(knee.x * w)
        knee_y = int(knee.y * h)

        cv2.putText(
            frame,
            f"Angle: {int(angle)}",
            (knee_x - 50, knee_y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        # =================================================
        # DISPLAY REP COUNT
        # =================================================

        cv2.putText(
            frame,
            f"Reps: {counter}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # =================================================
        # DISPLAY STAGE
        # =================================================

        cv2.putText(
            frame,
            f"Stage: {stage}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

        # =================================================
        # DISPLAY FEEDBACK
        # =================================================

        cv2.putText(
            frame,
            f"Feedback: {feedback}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

        # =================================================
        # DISPLAY HIP DROP
        # =================================================

        cv2.putText(
            frame,
            f"Hip Drop: {hip_drop:.2f}",
            (20, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    # =====================================================
    # SHOW WINDOW
    # =====================================================

    cv2.imshow("AI Personal Trainer - Squat Analysis", frame)

    timestamp += 33

    # ESC key to quit
    if cv2.waitKey(1) & 0xFF == 27:
        break

# =========================================================
# CLEANUP
# =========================================================

cap.release()
cv2.destroyAllWindows()