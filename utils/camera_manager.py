import cv2
from PyQt6.QtCore import QThread, pyqtSignal

class CameraLoaderThread(QThread):
    # Yeh signal progress update (0 se 100) bheje ga main UI ko
    progress_signal = pyqtSignal(int)
    # Yeh signal camera object deliver karega jab load ho jaye
    camera_ready_signal = pyqtSignal(object)

    def run(self):
        # Step 1: Initialization shuru (10%)
        self.progress_signal.emit(10)
        
        # Step 2: Driver hardware connection hit karo (40%)
        self.progress_signal.emit(40)
        cap = cv2.VideoCapture(0)
        
        # Step 3: Warmup check logic (70%)
        self.progress_signal.emit(70)
        
        if cap is not None and cap.isOpened():
            # Success: 100% load completed
            self.progress_signal.emit(100)
            self.camera_ready_signal.emit(cap)
        else:
            # Fallback agar camera na mile to dummy open rakhne k liye
            self.progress_signal.emit(100)
            self.camera_ready_signal.emit(None)

class CameraManager:
    _cap = None
    _loader_thread = None

    @classmethod
    def start_preload(cls, progress_callback, completion_callback):
        """Splash screen isay call kregi camera background me open krny k liye"""
        if cls._cap is not None:
            # Agar pehle se open hy to direct 100% krdo
            progress_callback(100)
            completion_callback(cls._cap)
            return

        cls._loader_thread = CameraLoaderThread()
        cls._loader_thread.progress_signal.connect(progress_callback)
        cls._loader_thread.camera_ready_signal.connect(completion_callback)
        cls._loader_thread.camera_ready_signal.connect(cls._save_instance)
        cls._loader_thread.start()

    @classmethod
    def _save_instance(cls, cap_object):
        cls._cap = cap_object

    @classmethod
    def get_camera(cls):
        """Saari screens direct yahan se object uthaen gi without reload"""
        return cls._cap

    @classmethod
    def release_camera(cls):
        """App bilkul exit krty waqt hardware free krny k liye"""
        if cls._cap is not None:
            if cls._cap.isOpened():
                cls._cap.release()
            cls._cap = None