import pyttsx3
import threading

class BaseExercise:

    def __init__(self):
        self.counter = 0
        self.stage = "up"

        self.feedback = "None"
        self.previous_feedback = "None"

        self.is_speaking = False

    def process(self, landmarks):
        raise NotImplementedError
    
    def async_audio(self, message):
        self.is_speaking = True

        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)

            engine.say(message)
            engine.runAndWait()
            
        finally:
            self.is_speaking = False
    
    def audio_feedback(self):
        if not self.is_speaking and self.feedback != "Standing" and self.feedback != self.previous_feedback:
            self.previous_feedback = self.feedback
            threading.Thread(target=self.async_audio, args=(self.feedback,)).start()
            
