from core.angle_calculator import calculate_angle
from core.exercises.base_exercise import BaseExercise


class SquatAnalyzer(BaseExercise):

    def __init__(self):

        super().__init__()

        self.initial_hip_y = None

    def process(self, landmarks):

        hip_l = landmarks[23]
        knee_l = landmarks[25]
        ankle_l = landmarks[27]

        hip_r = landmarks[24]
        knee_r = landmarks[26]
        ankle_r = landmarks[28]

        # LEFT ANGLE
        left_angle = calculate_angle(
            (hip_l.x, hip_l.y),
            (knee_l.x, knee_l.y),
            (ankle_l.x, ankle_l.y)
        )

        # RIGHT ANGLE
        right_angle = calculate_angle(
            (hip_r.x, hip_r.y),
            (knee_r.x, knee_r.y),
            (ankle_r.x, ankle_r.y)
        )

        # AVERAGE
        avg_angle = (
            left_angle + right_angle
        ) / 2

        # SYMMETRY
        symmetry_diff = abs(
            left_angle - right_angle
        )

        # INITIAL HIP POSITION
        if self.initial_hip_y is None:
            self.initial_hip_y = hip_l.y

            #self.initial_hip_y = (
            #    hip_l.y + hip_r.y
            #) / 2

        #current_hip_y = (
        #    hip_l.y + hip_r.y
        #) / 2

        hip_drop = hip_l.y - self.initial_hip_y
        #hip_drop = (
        #    current_hip_y -
        #    self.initial_hip_y
        #)

        # ===================================
        # FEEDBACK + REP LOGIC
        # ===================================

        if symmetry_diff > 20:
            self.feedback = "Balance Your Weight"

        elif avg_angle < 100 and hip_drop > 0.18:
            self.feedback = "Lower Your Hips"

        elif avg_angle < 70 and hip_drop > 0.28:
            self.stage = "down"
            self.feedback = "Good Form"

        else:
            self.feedback = "None"

        if (
            avg_angle > 160 and
            hip_drop < 0.05 and
            self.stage == "down"
        ):

            self.stage = "up"
            self.counter += 1
            self.feedback = "Good Rep"

        return {
            "counter": self.counter,
            "stage": self.stage,
            "feedback": self.feedback,
            "left_angle": left_angle,
            "right_angle": right_angle,
            "avg_angle": avg_angle,
            "symmetry": symmetry_diff,
            "hip_drop": hip_drop
        }