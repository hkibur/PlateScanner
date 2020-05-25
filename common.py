import time

def set_ind_red(widget):
    if widget.styleSheet() != "background: \"red\";":
        widget.setStyleSheet("background: \"red\";")
    widget.update()

def set_ind_yellow(widget):
    if widget.styleSheet() != "background: \"yellow\";":
        widget.setStyleSheet("background: \"yellow\";")
    widget.update()

def set_ind_green(widget):
    if widget.styleSheet() != "background: \"lightgreen\";":
        widget.setStyleSheet("background: \"lightgreen\";")
    widget.update()

def set_ind_condition(ind, cond):
    if cond:
        set_ind_green(ind)
    else:
        set_ind_red(ind)

def set_ind_threeway(ind, cond1, cond2):
    if cond1:
        if cond2:
            set_ind_green(ind)
        else:
            set_ind_yellow(ind)
    else:
        set_ind_red(ind)

def thread_delta_sleep(before, window):
    delta = time.time() - before
    if delta < window:
        time.sleep(window - delta)
