import Tkinter as tk
import ttk
import cv2
import numpy

MD200_RES_SETTING = {
#   (width, height, fps)
    (800, 600, 20),
    (1280, 960, 7.5),
    (1280, 1024, 7.5),
    (1600, 1200, 5)
}

class ScopeFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.res_setts = MD200_RES_SETTING
        self.cam = None
        
        self.rowconfigure(0, weight = 1)

        self.image_canvas = tk.Canvas(self)
        self.image_canvas.grid(row = 0, column = 0, sticky = tk.NSEW)

        self.setting_frame = tk.Frame(self)
        self.setting_frame.grid(row = 1, column = 0, sticky = tk.NSEW)
        

    def error_write(self, message):
        pass

    def status_write(self, message):
        pass

    def select_res(self, index):
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.res_setts[index][0])
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.res_setts[index][1])
        self.cam.set(cv2.cv.CV_CAP_PROP_FPS, self.res_setts[index][2])

    def bind_camera(self):
        try:
            self.cam = cv2.VideoCapture(0)
        except Exception as e:
            self.error_write("Can't bind camera: %s" % (e.message))
        if not self.cam.isOpened():
            self.error_write("Camera not opened!")
        self.select_res(0) # Select smallest resolution, highest framerate
        self.status_write("Opened camera at res setting %dx%d, %f fps" % (self.res_setts[0][0], self.res_setts[0][1], self.res_setts[0][2]))
