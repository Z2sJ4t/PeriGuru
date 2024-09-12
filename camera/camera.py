import cv2
import numpy as np
import math
import time
from itertools import combinations
import threading
from collections import deque

from camera.utils import resize, USM_sharp, show_image

CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

MAX_BUFFER = 15

def intersection_Hough(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if(div == 0):
        return -1, -1
    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def dist(p1, p2):
        return math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0])
            + (p1[1] - p2[1]) * (p1[1] - p2[1]))

def remove_close_lines(lines, min_diff = 20):
    res_lines = []
    for line1 in lines:
        flag = True
        for i in range(len(res_lines)):
            line2 = res_lines[i]
            dis1 = dist(line1[0], line2[0])
            dis2 = dist(line1[1], line2[1])
            if(dis1 < min_diff and dis2 < min_diff):
                p0 = ((line1[0][0] + line2[0][0]) / 2.0, (line1[0][1] + line2[0][1]) / 2.0)
                p1 = ((line1[1][0] + line2[1][0]) / 2.0, (line1[1][1] + line2[1][1]) / 2.0)
                res_lines[i] = (p0, p1)
                flag = False
                break
        if(flag):
            res_lines.append(line1)
    return res_lines

def four_point_transform(img, pts):
    pt_sum = pts.sum(axis = 1)
    pt_diff = np.diff(pts, axis = 1)
    tl, br = pts[np.argmin(pt_sum)], pts[np.argmax(pt_sum)]
    tr, bl= pts[np.argmin(pt_diff)], pts[np.argmax(pt_diff)]
    
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32") 
    rect = np.array([tl, tr, br, bl], dtype = "float32").reshape(4, 2)
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
    return warped

def RhoTheta2xy(lines, max_x, max_y):
    res_lines = []
    for line in lines:
        rho, theta = line[0]
        xy = []
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        x0 = rho * cos_theta
        y0 = rho * sin_theta
        if(abs(sin_theta) > 0.001):
            yy = rho / sin_theta
            if(yy > 0 and yy < max_y):
                xy.append((0, yy))
        if(abs(cos_theta) > 0.001):
            xx = rho / cos_theta
            if(xx > 0 and xx < max_x):
                xy.append((xx, 0))
        if(abs(sin_theta) > 0.001):
            yy = y0 - (max_x - x0) / sin_theta * cos_theta
            if(yy > 0 and yy < max_y):
                xy.append((max_x, yy))
        if(abs(cos_theta) > 0.001):
            xx = x0 - (max_y - y0) / cos_theta * sin_theta
            if(xx > 0 and xx < max_x):
                xy.append((xx, max_y))
        res_lines.append(xy)
    return res_lines

class Camera:
    def __init__(self):
        # screen anchors
        self.pts = np.zeros((4, 2))
        self.anchors = [(0, 0), (960, 0), (960, 540), (0, 540)]
        # ===========Multi threaded camera operation===========
        self.img_q = deque([], MAX_BUFFER)
        self.read_camera_thread = Camera.readCameraThread(self)
        self.threading_lock = threading.Lock()

    def closest_intersection_point(self, lines, max_x, max_y):
        points = [[0, 0], [max_x, 0], [0, max_y], [max_x, max_y]]
        for line1, line2 in combinations(lines, 2):
            x, y = intersection_Hough(line1, line2)
            if(x > 0 and x < max_x and y > 0 and y < max_y):
                p = [x, y]
                for i in range(4):
                    if(dist(p, self.anchors[i]) < dist(points[i], self.anchors[i])):
                        points[i] = p
        return np.array(points)

    def anchor_screen_area(self, orig_img, show=False, scale=0.5):
        # Scale down the original image to accelerate the process of finding screen range
        img = cv2.resize(orig_img, None, fx=scale, fy=scale)
        # Pre processing before edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Convert to grayscale image
        gray = cv2.medianBlur(gray, 5) # medianBlur can protect image edges 
        canny = cv2.Canny(gray, threshold1=50, threshold2=150) # Canny edge detection
        # Hough line transformation is more robust than edge detection when anchoring screen area
        lines = cv2.HoughLines(canny, 1, np.pi/180, 120)
        lines = RhoTheta2xy(lines, img.shape[1], img.shape[0])
        #lines = remove_close_lines(lines)
        
        if(show):
            for line in lines:
                p1, p2 = line
                cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (255, 0, 0), 2)
            show_image(img)

        self.pts = \
            self.closest_intersection_point(lines, img.shape[1], img.shape[0]) / scale

    def anchor(self, scale=0.5):
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1) # auto focus
        time.sleep(2)

        count = 0
        anchor_flag = False

        cv2.namedWindow("Camera")

        while(True):
            ret, orig_img = cap.read()
            img = cv2.resize(orig_img, None, fx=scale, fy=scale)

            def mouse_callback(event, x, y, flags, param):
                nonlocal count
                if(event == cv2.EVENT_LBUTTONDOWN):
                    if(count < 4):
                        self.anchors[count] = (x, y)
                        count += 1

            if(not anchor_flag):
                if(count == 4):
                    print('begin to anchor!')
                    self.anchor_screen_area(orig_img, scale=scale)
                    anchor_flag = True
                else:
                    for i in range(count):
                        cv2.circle(img, self.anchors[i], 5, (0, 255, 0), -1)
            
            if(anchor_flag):
                for i in range(4):
                    p1 = self.pts[i] * scale
                    p2 = self.pts[(i + 1) % 4] * scale
                    cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (255, 0, 0), 2)

            cv2.imshow("Camera", img)
            cv2.setMouseCallback("Camera", mouse_callback)

            c = cv2.waitKey(1)
            if(c==13): # enter
                if(count==4):
                    break
            elif(c==32): # space
                anchor_flag = False
                count = 0
            elif(c==27): # ESC
                break                
                    
        cv2.destroyWindow("Camera") # Close window
        cap.release() # Relase camera capture

    class readCameraThread(threading.Thread):
        def __init__(self, outer_instance):
            super(Camera.readCameraThread).__init__()
            self.outer_instance = outer_instance
            self.stopFlag = True
            threading.Thread.__init__(self)
        
        def run(self):
            cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            time.sleep(2)

            while(self.stopFlag):
                ret, orig_img = cap.read()
                # Perspective transformation
                warped_img = four_point_transform(orig_img, self.outer_instance.pts)
                # Rotate 90 degrees
                warped_img = cv2.rotate(warped_img, cv2.ROTATE_90_CLOCKWISE)
                #warped_img = warped_img[20:-5, 5:-5, :]
                warped_img = USM_sharp(warped_img) # sharp image

                # Put frames into buffer
                self.outer_instance.threading_lock.acquire()
                if(len(self.outer_instance.img_q) == MAX_BUFFER):
                    self.outer_instance.img_q.popleft()
                self.outer_instance.img_q.append(warped_img)
                self.outer_instance.threading_lock.release()

            cap.release() 
            self.outer_instance.img_q.clear()
            
    def release_cam(self):
        self.read_camera_thread.stopFlag = False
        self.read_camera_thread.join() # Wait subthreading to exit

    def get_screen(self):
        flag = False
        ret_img = None

        while(not flag):
            self.threading_lock.acquire()
            if(len(self.img_q) > 0):
                flag = True
                ret_img = self.img_q.pop()
            self.threading_lock.release()
            # Wait until frames are fed into the buffer
            if(not flag):
                time.sleep(0.1)

        return ret_img

    def restart_cam(self):
        self.read_camera_thread.start()