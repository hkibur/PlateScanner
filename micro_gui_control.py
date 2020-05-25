import common

class MicroGuiControl(object):
    def __init__(self, ui, scanner_control):
        self.ui = ui
        self.sc = scanner_control

        self.ui.res_list.addItems(["{}x{} at {} fps".format(w, h, fps) for w, h, fps in self.sc.micro_control.DEFAULT_RES_SETTING])
        self.ui.set_res_button.clicked.connect(lambda: self.set_res())
        self.ui.start_feed_button.clicked.connect(lambda: self.start_feed())
        self.ui.stop_feed_button.clicked.connect(lambda: self.stop_feed())
        self.ui.start_feed_button.setDisabled(True)
        self.ui.fps_spin.setValue(self.sc.micro_control.fps_cap)
        self.ui.fps_spin.valueChanged.connect(lambda val: self.change_fps(val))

        self.sc.cron.add_job(0.5, self.update_stats)

    def update_stats(self):
        mc = self.sc.micro_control
        common.set_ind_condition(self.ui.micro_conn_ind, mc.is_connected())
        common.set_ind_threeway(self.ui.feed_run_ind, mc.is_connected(), not mc.feed_stop)
        self.ui.avg_fps_stat.setText(str(mc.average_fps))
        self.ui.total_frame_stat.setText(str(mc.total_frames))

    def set_res(self):
        self.stop_feed()
        print("resetting resolution")
        row_index = self.ui.res_list.row(self.ui.res_list.selectedItems()[0])
        if self.sc.micro_control.current_cam_index is None:
            print("Camera hasn't been connected, can't set resolution")
            return
        self.sc.micro_control.disconnect()
        self.sc.micro_control.connect(self.sc.micro_control.current_cam_index, row_index)
        self.start_feed()

    def start_feed(self):
        self.sc.micro_control.feed_stop = False
        self.ui.start_feed_button.setDisabled(True)
        self.ui.stop_feed_button.setEnabled(True)

    def stop_feed(self):
        self.sc.micro_control.feed_stop = True
        self.ui.start_feed_button.setEnabled(True)
        self.ui.stop_feed_button.setDisabled(True)

    def change_fps(self, val):
        self.sc.micro_control.fps_cap = val