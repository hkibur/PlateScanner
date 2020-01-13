import Tkinter as tk
import ttk
import cv2
import numpy

MD200_RES_SETTING = (
#   (width, height, fps)
    (800, 600, 20),
    (1280, 960, 7.5),
    (1280, 1024, 7.5),
    (1600, 1200, 5)
)

class ScopeFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.res_setts = MD200_RES_SETTING
        self.cam = None
        
        self.rowconfigure(0, weight = 1)

        self.image_canvas = tk.Canvas(self)
        self.image_canvas.grid(row = 0, column = 0, sticky = tk.NSEW)

        self.status_label = tk.Label(self, anchor = tk.W)
        self.status_label.grid(row = 1, column = 0, sticky = tk.NSEW)

        setting_frame = tk.Frame(self)
        setting_frame.grid(row = 2, column = 0, sticky = tk.NSEW)

        tk.Label(setting_frame, text = "Resolution/FPS: ").pack(side = tk.LEFT)
        self.res_combo = ttk.Combobox(setting_frame)
        self.res_combo.pack(side = tk.LEFT)
        self.res_combo.bind("<<ComboboxSelected>>", self.select_res)

        self.bind_camera()

    def error_write(self, message):
        self.status_label.config(text = message, fg = "#FF0000")

    def status_write(self, message):
        self.status_label.config(text = message, fg = "#000000")

    def select_res(self, *args, **kwargs):
        index = self.res_combo.current()
        # self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.res_setts[index][0])
        # self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.res_setts[index][1])
        # self.cam.set(cv2.cv.CV_CAP_PROP_FPS, self.res_setts[index][2])
        self.status_write("Opened camera at res setting %dx%d, %.2f fps" % (self.res_setts[index][0], self.res_setts[index][1], self.res_setts[index][2]))

    def bind_camera(self):
        # try:
        #     self.cam = cv2.VideoCapture(0)
        # except Exception as e:
        #     self.error_write("Can't bind camera: %s" % (e.message))
        # if not self.cam.isOpened():
        #     self.error_write("Camera not opened!")

        combo_list = []
        for width, height, fps in self.res_setts:
            combo_list.append("%dx%d, %f fps" % (width, height, fps))
        self.res_combo.config(values = combo_list)

        self.res_combo.current(0)
