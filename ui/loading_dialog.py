from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QColor

class ModernCircleSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.angle = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(15)

    def rotate(self):
        self.angle = (self.angle + 4) % 360
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
        rect = QRect(5, 5, 50, 50) 

        bg_pen = QPen(QColor("#1e293b")) 
        bg_pen.setWidth(5)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)

        accent_pen = QPen(QColor("#38bdf8")) 
        accent_pen.setWidth(5)
        accent_pen.setCapStyle(Qt.PenCapStyle.RoundCap) 
        painter.setPen(accent_pen)
        painter.drawArc(rect, -self.angle * 16, 120 * 16)


class LoadingDialog(QDialog):
    loading_finished = pyqtSignal()

    def __init__(self, exercise_name, parent=None, status1=None, status2=None, duration=3200):
        super().__init__(parent)
        
        if status1 is None:
            status1 = (
                "<span style='font-size:22px; font-weight:bold;'>Preparing Session</span><br>"
                "<span style='font-size:14px; color:#cbd5e1; font-weight:normal;'>"
                "Stand in front of Camera in correct Position.</span>"
            )
        if status2 is None:
            status2 = "Initializing AI Environment..."

        self.setFixedSize(360, 260)
        
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 360, 260)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border: 2px solid #38bdf8;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(25, 20, 25, 20)

        self.title_lbl = QLabel(f"{exercise_name}", self.container)
        self.title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #38bdf8; border: none; background: transparent;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner = ModernCircleSpinner(self.container)
        self.spinner.setStyleSheet("border: none; background: transparent;")

        self.status_lbl = QLabel(status1, self.container)
        self.status_lbl.setStyleSheet("font-size: 18px; font-weight: 600; color: #f2f4f7; margin-top: 5px; border: none; background: transparent;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_lb2 = QLabel(status2, self.container)
        self.status_lb2.setStyleSheet("font-size: 14px; color: #94a3b8; margin-top: 2px; border: none; background: transparent;")
        self.status_lb2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(12)
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter) 
        layout.addSpacing(12)
        layout.addWidget(self.status_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(4) 
        layout.addWidget(self.status_lb2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.start_pop_out)
        self.main_timer.start(duration)

    def showEvent(self, event):
        """🔥 Fixed: Pure Vertical Slide Up Pop-In from Bottom"""
        super().showEvent(event)
        
        # Fade In
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()

        # Pure Vertical Animation (X const rakh ke sirf Y animate ho rha hy)
        orig_geo = self.geometry()
        self.scale_anim = QPropertyAnimation(self, b"geometry")
        self.scale_anim.setDuration(300)
        # Start state: Niche se shuru hoga (Y + 80) aur height zero hogi
        self.scale_anim.setStartValue(QRect(orig_geo.x(), orig_geo.y() + 80, orig_geo.width(), 0))
        self.scale_anim.setEndValue(orig_geo)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack) # Premium smooth bounce
        self.scale_anim.start()

    def start_pop_out(self):
        """🔥 Fixed: Pure Vertical Slide Down Pop-Out"""
        self.main_timer.stop()
        
        self.out_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.out_fade.setDuration(250)
        self.out_fade.setStartValue(1.0)
        self.out_fade.setEndValue(0.0)
        
        orig_geo = self.geometry()
        self.out_scale = QPropertyAnimation(self, b"geometry")
        self.out_scale.setDuration(250)
        self.out_scale.setStartValue(orig_geo)
        # End state: Niche ki taraf collapse ho jayega
        self.out_scale.setStartValue(orig_geo)
        self.out_scale.setEndValue(QRect(orig_geo.x(), orig_geo.y() + 80, orig_geo.width(), 0))
        self.out_scale.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.out_fade.finished.connect(self.finish_loading)
        
        self.out_fade.start()
        self.out_scale.start()

    def finish_loading(self):
        self.loading_finished.emit()
        self.accept()