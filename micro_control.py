import cv2
import threading

DEFAULT_FPS_CAP = 10

class MicroControl(object):
    def __init__(self):
        self.cam_handle = None
        self.current_cam_index = None

        self.fps_cap = DEFAULT_FPS_CAP
        self.total_frames = 0
        self.average_fps = 0

        self.feed_stop = False

        self.DEFAULT_RES_SETTING = (
            (1600, 1200, 1),
            (1280, 960, 1),
            (640, 480, 1),
            (352, 288, 1),
            (320, 240, 1),
            (160, 120, 1),
        )

    def connect(self, index, res_index):
        self.current_cam_index = index
        try:
            cam = cv2.VideoCapture(index)
            self.cam_handle = cam
        except Exception as e:
            print("cant open camera for some reason")
            return
            
    def disconnect(self):
        if self.cam_handle is not None:
            self.cam_handle.release()
            self.cam_handle = None

    def is_connected(self):
        return self.cam_handle is not None

    def get_frame(self):
        if self.cam_handle is None:
            print("Can't capture frame, camera not bound!")
            return None
        stat, frame = self.cam_handle.read()
        if not stat:
            print("Frame caputure not successful!")
            return None
        self.total_frames += 1
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
