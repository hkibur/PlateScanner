import common
import cv2
import time
from PyQt5 import QtCore as qt_core
from PyQt5 import QtGui as qt_gui

PUMP_PAUSE_TIME = 0.5

# This is more closely connected with the GUI that micro control so it makes more sense to have it here
class MicroVideoPump(qt_core.QThread):
    def __init__(self, video_widget, micro_control):
        super().__init__()
        self.video_widget = video_widget
        self.micro_control = micro_control
        self.thread_stop = False

    def close(self):
        self.thread_stop = True
        self.wait()

    def run(self):
        while not self.thread_stop:
            now = time.time()
            if not (self.micro_control.is_connected() and not self.micro_control.feed_stop):
                common.thread_delta_sleep(now, PUMP_PAUSE_TIME)
                continue
            frame = self.micro_control.get_frame()
            if frame is not None:
                # from https://stackoverflow.com/a/55468544/6622587 bcuz im dumb :^(
                h, w, ch = frame.shape
                bytesPerLine = ch * w
                qImg = qt_gui.QImage(frame.data, w, h, bytesPerLine, qt_gui.QImage.Format_RGB888)
                self.video_widget.setPixmap(qt_gui.QPixmap.fromImage(qImg))
            common.thread_delta_sleep(now, 1 / self.micro_control.fps_cap)

class ScannerGuiControl(object):
    def __init__(self, ui, scanner_control):
        self.ui = ui
        self.sc = scanner_control

        self.micro_pump = MicroVideoPump(self.ui.micro_video, self.sc.micro_control)
        self.micro_pump.start()

        self.ui.scaling_reset.clicked.connect(lambda: self.sc.do_scaling())

    def update_stat(self):
        pass