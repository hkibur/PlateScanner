import cv2

import common

CALIB_MOVEMENT_AMT = 10

LOWE_RATIO_CONSTANT = 0.75

def lowe_ratio_test(self, matches):
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
    return train_points, query_points

class Prog(object):
    def __init__(self, scanner, micro):
        self.scanner = scanner
        self.micro = micro

        self.orb = cv2.ORB()
        self.bf = cv2.BFMatcher()

    def calibrate(self):
        self.scanner.move_to_origin()
        start_frame = cv2.cvtColor(self.micro.get_frame(), cv2.COLOR_BGR2GRAY)
        self.scanner.step(CALIB_MOVEMENT_AMT, 0)
        end_x_frame = cv2.cvtColor(self.micro.get_frame(), cv2.COLOR_BGR2GRAY)
        self.scanner.step(0, CALIB_MOVEMENT_AMT)
        end_y_frame = cv2.cvtColor(self.micro.get_frame(), cv2.COLOR_BGR2GRAY)
        self.scanner.move_to_origin()

        start_kp, start_des = self.orb.detectAndCompute(start_frame, None)
        end_x_kp, end_x_des = self.orb.detectAndCompute(end_x_frame, None)
        end_y_kp, end_y_des = self.orb.detectAndCompute(end_y_frame, None)

        x_matches = lowe_ratio_test(self.bf.knnMatch(end_x_des, start_des, 2))
        y_matches = lowe_ratio_test(self.bf.knnMatch(end_y_des, end_x_des, 2))

        x_matrix = None
        y_matrix = None

        if len(x_matches) >= 3:
            x_matrix = cv2.estimateAffinePartial2D(*get_match_points(x_matches, start_kp, end_x_kp))
        else:
            common.error("Calibration: not enough X matches for limited affine transformation: %d, need at least 3" % (len(x_matches)))

        if len(y_matches) >= 3:
            y_matrix = cv2.estimateAffinePartial2D(*get_match_points(y_matches, end_x_kp, end_y_kp))
        else:
            common.error("Calibration: not enough Y matches for limited affine transformation: %d, need at least 3" % (len(y_matches)))

        print x_matrix
        print y_matrix

    def scan(self):
        pass