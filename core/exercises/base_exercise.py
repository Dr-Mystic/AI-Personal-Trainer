import pyttsx3

class BaseExercise:

    def __init__(self,):
        self.counter = 0
        self.stage = "up"
        self.feedback = "None"
        self.previous_feedback = "None"

    def process(self, landmarks):
        raise NotImplementedError
    
    def audio_feedback(self):
        if self.feedback != "Standing" and self.feedback != self.previous_feedback:
            self.previous_feedback = self.feedback
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)

            engine.say(self.feedback)
            engine.runAndWait()
