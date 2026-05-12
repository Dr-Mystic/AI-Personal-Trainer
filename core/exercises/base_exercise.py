class BaseExercise:

    def __init__(self):

        self.counter = 0
        self.stage = "up"
        self.feedback = "None"

    def process(self, landmarks):

        raise NotImplementedError