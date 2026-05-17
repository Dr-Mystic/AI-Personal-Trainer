import cv2

from core.pose_detector import PoseDetector
from core.exercises.crunch_analyzer import CrunchAnalyzer
from core.drawing_utils import draw_landmarks

pose_detector = PoseDetector()
crunch_analyzer = CrunchAnalyzer()

cap = cv2.VideoCapture(0)

cap.set(3, 1920)
cap.set(4, 1080)

timestamp = 0

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    result = pose_detector.detect(frame, timestamp)

    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        data = crunch_analyzer.process(landmarks)

        crunch_analyzer.audio_feedback()

        draw_landmarks(frame, landmarks)

        cv2.putText(
            frame,
            f"Reps: {data['counter']}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Stage: {data['stage']}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Torso Angle: {int(data['torso'])}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Knee Angle: {int(data['avg_knee'])}",
            (20, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            f"Feedback: {data['feedback']}",
            (20, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

    cv2.imshow("AI Personal Trainer", frame)

    timestamp += 33

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()