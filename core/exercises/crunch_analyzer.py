from core.angle_calculator import calculate_angle
from core.exercises.base_exercise import BaseExercise


class CrunchAnalyzer(BaseExercise):

    def __init__(self):
        super().__init__()

        self.up_threshold = 150
        self.down_threshold = 100

        self.stage = "None"

    def get_midpoint(self, a, b):
        return (
            (a.x + b.x) / 2,
            (a.y + b.y) / 2
        )

    def process(self, landmarks):

        shoulder_l = landmarks[11]
        shoulder_r = landmarks[12]

        hip_l = landmarks[23]
        knee_l = landmarks[25]
        ankle_l = landmarks[27]

        hip_r = landmarks[24]
        knee_r = landmarks[26]
        ankle_r = landmarks[28]

        nose = landmarks[0]

        shoulder_mid = self.get_midpoint(shoulder_l, shoulder_r)
        hip_mid = self.get_midpoint(hip_l, hip_r)

        torso_angle = calculate_angle(
            shoulder_mid,
            hip_mid,
            (hip_mid[0], hip_mid[1] + 1e-3)
        )

        left_knee_angle = calculate_angle(
            (hip_l.x, hip_l.y),
            (knee_l.x, knee_l.y),
            (ankle_l.x, ankle_l.y)
        )

        right_knee_angle = calculate_angle(
            (hip_r.x, hip_r.y),
            (knee_r.x, knee_r.y),
            (ankle_r.x, ankle_r.y)
        )

        avg_knee_angle = (left_knee_angle + right_knee_angle) / 2

        if (avg_knee_angle < 45):

            if torso_angle > self.up_threshold and self.stage == "down":
                self.counter += 1
                self.stage = "up"
                self.feedback = "Good crunch"

            elif torso_angle < self.down_threshold:
                self.stage = "down"
                self.feedback = "Contract core"

            neck_offset = abs(nose.x - shoulder_mid[0])
            if neck_offset > 0.1:
                self.feedback = "Stop pulling neck"

            if torso_angle < 90:
                self.stage = "Laying down"
                self.feedback = "Don't lay back"
        
        else:
            self.feedback = "Bring up your legs"

        return {
            "counter": self.counter,
            "stage": self.stage,
            "torso": torso_angle,
            "avg_knee": avg_knee_angle,
            "feedback": self.feedback
        }