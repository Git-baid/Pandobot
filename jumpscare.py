# for jumpscare
import sys
import ctypes
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel

image_duration = 2000
fade_duration = 1000
GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
user32 = ctypes.windll.user32

image_path = "jumpscare.png"
if len(sys.argv) > 1:
    image_path = sys.argv[1]
duration = 1000
if len(sys.argv) > 2:
    duration = int(sys.argv[2])


app = QApplication(sys.argv)

overlay = QLabel()
overlay.setWindowFlags(
    Qt.WindowType.FramelessWindowHint
    | Qt.WindowType.Tool
    | Qt.WindowType.WindowStaysOnTopHint
)
overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
overlay.setGeometry(0, 0, 2560, 1440)
overlay.showFullScreen()

pixmap = QPixmap(image_path).scaled(
    2560,
    1440,
    Qt.AspectRatioMode.IgnoreAspectRatio,
    Qt.TransformationMode.SmoothTransformation,
)

image = QLabel(overlay)
image.setPixmap(pixmap)
image.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
image.adjustSize()
image.move(1440, 0)
image.show()

animation = QPropertyAnimation(overlay, b"windowOpacity")
animation.setDuration(fade_duration)
animation.setStartValue(1.0)
animation.setEndValue(0.0)
animation.setEasingCurve(QEasingCurve.Type.OutQuad)

def start_fade():
    animation.start()
    
# Add WS_EX_NOACTIVATE so the window won't steal focus
# Get the window handle (HWND) of the label (ID of the window)
hwnd = int(overlay.winId())

# Asks Windows what are this window's current extended styles, adds the WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, and WS_EX_TOPMOST styles, and sets the new styles back to the window.
style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
# WS_EX_NOACTIVATE = Doesnt focus the window when it is shown
# WS_EX_TOOLWINDOW = Creates a tool window which doesnt show up in alt+tab/taskbar
# WS_EX_TOPMOST = Makes the window stay on top of all other windows
style |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST
user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

# Close the jumpscare after the specified duration
QTimer.singleShot(image_duration, start_fade)

animation.finished.connect(app.quit)
sys.exit(app.exec())