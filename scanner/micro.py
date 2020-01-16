import cv2
import numpy
import time

MD200_RES_SETTING = (
#   (width, height, fps)
    (800, 600, 20),
    (1280, 960, 7.5),
    (1280, 1024, 7.5),
    (1600, 1200, 5)
)

TEST_WEBCAM_RES_SETTING = (
    (160, 120, 1),
    (320, 240, 1),
    (352, 288, 1),
    (640, 480, 1),
    (1280, 960, 1),
    (1600, 1200, 1),
)


class Microscope(object):
    def __init__(self):
        self.res_setts = MD200_RES_SETTING
        self.cam = None
        self.cur_frame = None
        self.cam_index = None

    def set_index(self, index):
        self.cam_index = index

    def reset_camera(self):
        if self.cam is not None:
            self.cam.release()
        try:
            self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        except Exception:
            return False
        if self.cam is None:
            return False
        return True

    def select_res(self, index):
        self.reset_camera()
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.res_setts[index][0])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res_setts[index][1])
        self.cam.set(cv2.CAP_PROP_FPS, self.res_setts[index][2])
        self.get_frame()

    def read_frame(self):
        status, frame = self.cam.read()
        if not status:
            return False
        self.cur_frame = frame

    def get_frame(self):
        if not self.read_frame():
            return None
        return self.cur_frame