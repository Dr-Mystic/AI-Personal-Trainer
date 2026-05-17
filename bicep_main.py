import cv2

from core.pose_detector import PoseDetector
from core.exercises.bicep_curl_analyzer import BicepCurlAnalyzer
from core.drawing_utils import draw_landmarks

pose_detector = PoseDetector()
bicep_analyzer = BicepCurlAnalyzer()

cap = cv2.VideoCapture(0)

cap.set(3, 1920)
cap.set(4, 1080)

timestamp = 0

while cap.isOpened():

    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    if not success:
        break

    result = pose_detector.detect(
        frame,
        timestamp
    )

    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        data = bicep_analyzer.process(
            landmarks
        )

        bicep_analyzer.audio_feedback()

        draw_landmarks(frame, landmarks)

        cv2.putText(
            frame,
            f"Left Reps: {data['right_counter']}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Right Reps: {data['left_counter']}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Left Stage: {data['right_stage']}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Right Stage: {data['left_stage']}",
            (20, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Left Angle: {int(data['right_angle'])}",
            (20, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Right Angle: {int(data['left_angle'])}",
            (20, 300),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Feedback: {data['feedback']}",
            (20, 350),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

    cv2.imshow(
        "AI Personal Trainer",
        frame
    )

    timestamp += 33

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()