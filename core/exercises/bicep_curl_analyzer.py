from core.angle_calculator import calculate_angle
from core.exercises.base_exercise import BaseExercise


class BicepCurlAnalyzer(BaseExercise):

    def __init__(self):

        super().__init__()

        # LEFT ARM
        self.left_counter = 0
        self.left_stage = "down"

        # RIGHT ARM
        self.right_counter = 0
        self.right_stage = "down"

    def process(self, landmarks):

        # ======================================
        # LEFT ARM LANDMARKS
        # ======================================

        left_shoulder = landmarks[11]
        left_elbow = landmarks[13]
        left_wrist = landmarks[15]

        # ======================================
        # RIGHT ARM LANDMARKS
        # ======================================

        right_shoulder = landmarks[12]
        right_elbow = landmarks[14]
        right_wrist = landmarks[16]

        # ======================================
        # LEFT ARM ANGLE
        # ======================================

        left_angle = calculate_angle(
            (left_shoulder.x, left_shoulder.y),
            (left_elbow.x, left_elbow.y),
            (left_wrist.x, left_wrist.y)
        )

        # ======================================
        # RIGHT ARM ANGLE
        # ======================================

        right_angle = calculate_angle(
            (right_shoulder.x, right_shoulder.y),
            (right_elbow.x, right_elbow.y),
            (right_wrist.x, right_wrist.y)
        )


        # ======================================
        # LEFT ARM LOGIC
        # ======================================

        if left_angle < 45 and self.left_stage == "down":

            self.left_stage = "up"
            self.feedback = "Lower Slowly"

        elif left_angle > 170:

            self.feedback = "Curl Up"

        elif left_angle > 150 and self.left_stage == "up":

            self.left_stage = "down"
            self.left_counter += 1
            self.feedback = "Good Rep"

        # ======================================
        # RIGHT ARM LOGIC
        # ======================================

        if right_angle < 45 and self.right_stage == "down":

            self.right_stage = "up"
            self.feedback = "Lower Slowly"

        elif right_angle > 170:

            self.feedback = "Curl Up"
        
        elif right_angle > 150 and self.right_stage == "up":

            self.right_stage = "down"
            self.right_counter += 1
            self.feedback = "Good Rep"

        return {
            "left_counter": self.left_counter,
            "right_counter": self.right_counter,
            "left_stage": self.left_stage,
            "right_stage": self.right_stage,
            "left_angle": left_angle,
            "right_angle": right_angle,
            "feedback": self.feedback
        }