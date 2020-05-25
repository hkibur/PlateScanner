import Tkinter as tk
import ttk
import cv2
import numpy
from PIL import Image, ImageTk
import time

RES_SETTING_SWEEP_STEP_WIDTH = 150

MD200_RES_SETTING = (
#   (width, height, fps)
    (640, 480, 20),
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

class ScopeFrame(tk.Frame):
    def __init__(self, parent, micro_obj, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.micro = micro_obj
        
        self.rowconfigure(0, weight = 1)

        self.image_canvas = tk.Canvas(self)
        self.image_canvas.grid(row = 0, column = 0, sticky = tk.NSEW)

        self.status_label = tk.Label(self, anchor = tk.W)
        self.status_label.grid(row = 1, column = 0, sticky = tk.NSEW)

        setting_frame = tk.Frame(self)
        setting_frame.grid(row = 2, column = 0, sticky = tk.NSEW)

        tk.Button(setting_frame, text = "Capture", command = self.draw_frame).pack(side = tk.LEFT)

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
        self.micro.select_res(index)
        self.status_write("Opened camera at res setting %dx%d, %.2f fps" % (self.micro.res_setts[index][0],
                                                                            self.micro.res_setts[index][1],
                                                                            self.micro.res_setts[index][2]))

    def bind_camera(self):
        # self.sweep_res_settings(3840, 2160)

        combo_list = []
        for width, height, fps in self.micro.res_setts:
            combo_list.append("%dx%d, %.2f fps" % (width, height, fps))
        self.res_combo.config(values = combo_list)

        self.res_combo.current(0)
        self.select_res()

    def sweep_res_settings(self, max_width, max_height):
        self.cam.release()
        max_width += max_width % RES_SETTING_SWEEP_STEP_WIDTH
        aspect = max_height / max_width
        for width in xrange(0, max_width, RES_SETTING_SWEEP_STEP_WIDTH):
            height = width * aspect
            self.cam = cv2.VideoCapture(0)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            frame = self.get_frame()
            if frame is None:
                continue
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            print img.width(), img.height()
            self.cam.release()

    def draw_frame(self):
        if not self.micro.get_frame():
            self.error_write("Frame caputure not successful!")
        frame = self.micro.cur_frame
        if frame is None:
            self.error_write("Frame is None??")
            return
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.cur_frame = ImageTk.PhotoImage(Image.fromarray(rgb_frame))
        self.image_canvas.delete("all")
        self.image_canvas.config(width = self.cur_frame.width(), height = self.cur_frame.height())
        self.image_canvas.create_image(0, 0, image = self.cur_frame, anchor = tk.NW)
        self.status_write("Frame captured %dx%d" % (self.cur_frame.width(), self.cur_frame.height()))

    def destroy(self):
        if self.micro.cam is not None:
            print "release"
            self.micro.cam.release()
        tk.Frame.destroy(self)
