import cv2
import mediapipe as mp
import numpy as np

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ====================================
# Angle Calculation Function
# ====================================

def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc)
    )

    angle = np.degrees(np.arccos(cosine_angle))

    return angle

# ====================================
# MediaPipe Setup
# ====================================

base_options = python.BaseOptions(
    model_asset_path="pose_landmarker_heavy.task"
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1
)

detector = vision.PoseLandmarker.create_from_options(options)

# ====================================
# Webcam
# ====================================

cap = cv2.VideoCapture(1)

timestamp = 0

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = detector.detect_for_video(
        mp_image,
        timestamp
    )

    h, w, _ = frame.shape

    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        # ====================================
        # LEFT LEG LANDMARKS
        # ====================================

        hip = landmarks[23]
        knee = landmarks[25]
        ankle = landmarks[27]

        hip_point = (hip.x, hip.y)
        knee_point = (knee.x, knee.y)
        ankle_point = (ankle.x, ankle.y)

        # ====================================
        # CALCULATE KNEE ANGLE
        # ====================================

        angle = calculate_angle(
            hip_point,
            knee_point,
            ankle_point
        )

        # ====================================
        # DRAW LANDMARKS
        # ====================================

        for landmark in landmarks:

            cx = int(landmark.x * w)
            cy = int(landmark.y * h)

            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        # ====================================
        # DISPLAY ANGLE
        # ====================================

        knee_x = int(knee.x * w)
        knee_y = int(knee.y * h)

        cv2.putText(
            frame,
            f"Knee Angle: {int(angle)}",
            (knee_x - 50, knee_y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    cv2.imshow("Angle Detection", frame)

    timestamp += 33

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()