from robot_movement.robot import Robot

import time
import cv2
import numpy as np

def cvt_pos(u, v, mat):
    x = (mat[0][0]*u + mat[0][1]*v + mat[0][2]) / (mat[2][0]*u + mat[2][1]*v + mat[2][2])
    y = (mat[1][0]*u + mat[1][1]*v + mat[1][2]) / (mat[2][0]*u + mat[2][1]*v + mat[2][2])
    return x, y

H1 = 12.5
H2 = 14.5

# left top, left bottom, right bottom, right top 
ANCHOR_POINTS = ((21, 4.5), (21, -4.5), (15, -4.5), (15, 4.5))

class Actuator:
    def __init__(self):
        self.robot = Robot()
        # 8.7 21.6
        # 9.2 10.5
        # -9 10.6
        # -9.4 21.3
        srcPoints = ((0, 0), (0, 1), (1, 1), (1, 0))
        dstPoints = ((21.6, 8.7), (21.3, -9.2), (10.6, -9.2), (10.5, 9.2))
        srcPoints = np.array(srcPoints, dtype = "float32").reshape(4, 2)
        dstPoints = np.array(dstPoints, dtype = "float32").reshape(4, 2)
        self.M = cv2.getPerspectiveTransform(srcPoints, dstPoints)

    def draw_cacalibration_points(self):
        for p in ANCHOR_POINTS:
            self.robot.move(p[1], p[0], H2, 1800)
            self.robot.move_height(H1, 600)
            time.sleep(0.1)
            self.robot.move_height(H2, 600)
            time.sleep(0.5)
        self.robot.observation_pos()

    def get_cacalibration_M(self, img_path, show=False):
        img = cv2.imread(img_path)
        height, width = img.shape[0], img.shape[1]
        gary = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gary, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 8)

        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        circles = []

        for c in contours:
            area = cv2.contourArea(c)
            if(area < 20 or area > 250):
                continue
            # Calculate the radius of the contour's circumscribed circle
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if(radius < 1 or radius > 15):
                continue
            circles.append((x / width, y / height))
        
        if(len(circles) < 4):
            return False

        circles = sorted(circles, key=lambda x: (x[0] - 0.5) ** 2 + (x[1] - 0.5) ** 2)
        circles = circles[:4]
        circles = sorted(circles, key=lambda x: x[0])
        # left top, left bottom, right bottom, right top 
        if(circles[0][1] > circles[1][1]):
            circles[0], circles[1] = circles[1], circles[0]
        if(circles[2][1] < circles[3][1]):
            circles[0], circles[1] = circles[1], circles[0]

        if(show):
            for c in circles:
                print(c[0], c[1])
                cv2.circle(img, (int(c[0] * width), int(c[1] * height)), 5, (0, 0, 255), -1)
            cv2.imshow('Black Points', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        srcPoints = np.array(circles, dtype = "float32").reshape(4, 2)
        dstPoints = np.array(ANCHOR_POINTS, dtype = "float32").reshape(4, 2)
        self.M = cv2.getPerspectiveTransform(srcPoints, dstPoints)
        print(self.M)
        return True

    def tap(self, x, y):
        yy, xx = cvt_pos(x, y, self.M)
        print('tap:', x, y, 'pos:', xx, yy)

        self.robot.move(xx, yy, H2, 1500)
        self.robot.move_height(H1, 600)
        time.sleep(0.15)
        self.robot.move_height(H2, 600)

    def long_press(self, x, y):
        yy, xx = cvt_pos(x, y, self.M)

        self.robot.move(xx, yy, H2, 1200)
        self.robot.move_height(H1, 600)
        time.sleep(0.6)
        self.robot.move_height(H2, 600)

    def scroll_up(self, x, y):
        yy, xx = cvt_pos(x, y, self.M)

        self.robot.move(xx, yy, H2, 1200)
        self.robot.move_height(H1, 600)
        self.robot.move_rotate(15, 600)
        self.robot.move_height(H2, 600)

    def scroll_down(self, x, y):
        yy, xx = cvt_pos(x, y, self.M)

        self.robot.move(xx, yy, H2, 1200)
        self.robot.move_height(H1, 600)
        self.robot.move_rotate(-15, 600)
        self.robot.move_height(H2, 600)

    def observation_pos(self):
        self.robot.observation_pos()
