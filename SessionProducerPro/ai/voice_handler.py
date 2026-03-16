# Author: Tresslers Group
import logging
import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)

class VoiceThread(QThread):
    transcription_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        
    def run(self):
        try:
            with sr.Microphone() as source:
                logger.info("VoiceThread: Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            logger.info("VoiceThread: Transcribing...")
            text = self.recognizer.recognize_google(audio)
            self.transcription_ready.emit(text)
            
        except sr.WaitTimeoutError:
            self.error_occurred.emit("Listening timed out.")
        except sr.UnknownValueError:
            self.error_occurred.emit("Could not understand audio.")
        except sr.RequestError as e:
            self.error_occurred.emit(f"Service error: {e}")
        except Exception as e:
            self.error_occurred.emit(str(e))

class VoiceHandler:
    """
    Manages voice-to-text interaction.
    """
    def __init__(self):
        self.thread = None

    def start_listening(self, on_ready_callback, on_error_callback):
        if self.thread and self.thread.isRunning():
            return
            
        self.thread = VoiceThread()
        self.thread.transcription_ready.connect(on_ready_callback)
        self.thread.error_occurred.connect(on_error_callback)
        self.thread.start()

