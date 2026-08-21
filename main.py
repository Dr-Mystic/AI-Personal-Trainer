import sys
from PyQt6.QtWidgets import QApplication

from ui.splash_screen import SplashScreen
from ui.calibration_screen import CalibrationScreen
from ui.select_exercise import SelectExercise
from utils.camera_manager import CameraManager # 👈 Imported Manager

def main():
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.showMaximized()

    # Screens initialization
    calibration = CalibrationScreen()
    select_exercise = None

    # ---------------- NAVIGATION ----------------

    def go_to_calibration():
        nonlocal calibration
        
        # Ab check krny ki zrort ni q k splash tabhi aage aye ga jb manager ready hoga
        splash.hide()
        calibration.activate_camera_stream() 
        
        calibration.showMaximized()

        try: calibration.btn.clicked.disconnect()
        except TypeError: pass
        calibration.btn.clicked.connect(go_to_select)

    def go_to_select():
        nonlocal select_exercise
        calibration.hide()

        select_exercise = SelectExercise(previous_screen=calibration)
        select_exercise.showMaximized()

        try: select_exercise.back_btn.clicked.disconnect()
        except TypeError: pass
        select_exercise.back_btn.clicked.connect(go_back_to_calibration)

    def go_back_to_calibration():
        if select_exercise:
            select_exercise.hide()
        calibration.showMaximized()

    splash.start_clicked.connect(go_to_calibration)

    # Executing application loop
    exit_code = app.exec()
    
    # 🔒 Clear hardware pipeline safely when user exits the system completely
    CameraManager.release_camera()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()