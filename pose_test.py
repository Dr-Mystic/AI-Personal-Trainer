import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# =========================
# Load Pose Landmarker
# =========================

base_options = python.BaseOptions(
    model_asset_path="pose_landmarker_heavy.task"
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1
)

detector = vision.PoseLandmarker.create_from_options(options)

# =========================
# Webcam
# =========================

cap = cv2.VideoCapture(0)

frame_timestamp = 0

while cap.isOpened():
    success, frame = cap.read()

    if not success:
        break

    # Mirror effect
    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert to MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Detect pose
    detection_result = detector.detect_for_video(
        mp_image,
        frame_timestamp
    )

    # Draw landmarks
    if detection_result.pose_landmarks:

        for pose_landmarks in detection_result.pose_landmarks:

            for landmark in pose_landmarks:

                h, w, _ = frame.shape

                cx = int(landmark.x * w)
                cy = int(landmark.y * h)

                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    # Show frame
    cv2.imshow("AI Personal Trainer - Pose Detection", frame)

    frame_timestamp += 33

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()