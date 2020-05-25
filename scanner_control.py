import cv2
import time
import threading
import numpy

import cron
import shield_control
import micro_control

CRON_DELTA = 0.25
LOWE_RATIO_CONSTANT = 0.75

def lowe_ratio_test(matches):
    good = []
    for m, n in matches:
        if m.distance < LOWE_RATIO_CONSTANT * n.distance:
            good.append(m)
    return good

def get_match_points(matches, train_kp, query_kp):
    train_points = []
    query_points = []
    for match in matches:
        train_points.append(train_kp[match.trainIdx].pt)
        query_points.append(query_kp[match.queryIdx].pt)
    return numpy.asarray(train_points), numpy.asarray(query_points)

class ScalingWorker(threading.Thread):
    def __init__(self, micro_control, bf, orb):
        super().__init__()
        self.bf = bf
        self.orb = orb
        self.micro_control = micro_control

    def run(self):
        # self.scanner.move_to_origin()
        start_frame = cv2.cvtColor(self.micro_control.get_frame(), cv2.COLOR_BGR2GRAY)
        print("move x")
        time.sleep(3)
        # self.scanner.step(CALIB_MOVEMENT_AMT, 0)
        end_x_frame = cv2.cvtColor(self.micro_control.get_frame(), cv2.COLOR_BGR2GRAY)
        print ("move y")
        time.sleep(3)
        # self.scanner.step(0, CALIB_MOVEMENT_AMT)
        end_y_frame = cv2.cvtColor(self.micro_control.get_frame(), cv2.COLOR_BGR2GRAY)
        print("OK")
        # self.scanner.move_to_origin()

        print("start")
        try:
            start_kp, start_des = self.orb.detectAndCompute(start_frame, None)
            end_x_kp, end_x_des = self.orb.detectAndCompute(end_x_frame, None)
            end_y_kp, end_y_des = self.orb.detectAndCompute(end_y_frame, None)
        except Exception as e:
            print(str(e))

        print("sdds")

        x_matches = lowe_ratio_test(self.bf.knnMatch(end_x_des, start_des, 2))
        y_matches = lowe_ratio_test(self.bf.knnMatch(end_y_des, end_x_des, 2))

        x_matrix = None
        y_matrix = None

        print("sdsad")

        if len(x_matches) >= 3:
            x_matrix = cv2.estimateAffinePartial2D(*get_match_points(x_matches, start_kp, end_x_kp))
            print(x_matrix[0])
        else:
            print("Calibration: not enough X matches for limited affine transformation: %d, need at least 3" % (len(x_matches)))

        if len(y_matches) >= 3:
            y_matrix = cv2.estimateAffinePartial2D(*get_match_points(y_matches, end_x_kp, end_y_kp))
            print(y_matrix[0])
        else:
            print("Calibration: not enough Y matches for limited affine transformation: %d, need at least 3" % (len(y_matches)))

class ScannerControl(object):
    def __init__(self):
        self.shield_control = shield_control.ShieldControl()
        self.micro_control = micro_control.MicroControl()

        self.cron = cron.ScannerCron(CRON_DELTA)

        self.orb = cv2.ORB_create()
        self.bf = cv2.BFMatcher()

    def do_scaling(self):
        worker = ScalingWorker(self.micro_control, self.bf, self.orb)
        worker.start()
        
    def translate(self, amt_x, amt_y):
        pass

    def move_to_origin(self):
        pass

    def close(self):
        self.shield_control.disconnect()
        self.micro_control.disconnect()
        self.cron.close()