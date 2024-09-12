from Arm_Lib import Arm_Device

import time
import math

L1 = 8.2
L2 = 8.2
L3 = 18
MAX_FRONT_DEG = 30

DE2RA = math.pi / 180
RA2DE = 180 / math.pi

def able_to_move(th1, th2, th3):
    if(th1 < 0.1 or th1 > 179.9):
        return False
    if(th2 < 0.1 or th2 > 179.9):
        return False
    if(th3 < 0.1 or th3 > 179.9):
        return False
    return True

def move_plane(Ax, Ay, gamma):
    Bx = Ax - L3 * math.cos(gamma)
    By = Ay + L3 * math.sin(gamma)
    lp = Bx * Bx + By * By
    sqlp = math.sqrt(lp)

    if(sqlp > L1 + L2):
        return False, -1, -1, -1
    
    alpha = math.atan2(By, Bx)
    beta = math.acos((lp + L1 * L1 - L2 * L2) / (2 * L1 * sqlp))
    th1 = -(math.pi / 2 - alpha - beta)
    th2 = math.acos((L1 * L1 + L2 * L2 - lp) / (2* L1 *L2)) - math.pi
    th3 = -th1 - th2 - math.pi / 2 - gamma
    return True, th1 * RA2DE + 90, th2 * RA2DE + 90, th3 * RA2DE + 90

def move_plane_enum_gamma(r, h):
    for gamma in range(MAX_FRONT_DEG):
        succ, th1, th2, th3 = move_plane(r, h, gamma * DE2RA)
        if(succ and able_to_move(th1, th2, th3)):
            #print('gamma=', gamma)
            return True, th1, th2, th3
        succ, th1, th2, th3 = move_plane(r, h, -gamma * DE2RA)
        if(succ and able_to_move(th1, th2, th3)):
            #print('gamma=', -gamma)
            return True, th1, th2, th3
    return False, -1, -1, -1

def forward_kinematics(deg1, deg2, deg3, deg4):
    deg1 = deg1 * DE2RA
    deg2 = (deg2 - 90) * DE2RA
    deg3 = (deg3 - 90) * DE2RA
    deg4 = (deg4 - 90) * DE2RA
    proj = L1 * math.sin(deg2) + L2 * math.sin(deg2 + deg3) + L3 * math.sin(deg2 + deg3 + deg4)
    h = L1 * math.cos(deg2) + L2 * math.cos(deg2 + deg3) + L3 * math.cos(deg2 + deg3 + deg4)
    x = -proj * math.cos(deg1)
    y = -proj * math.sin(deg1)
    return x, y, h

class Robot:
    # ID=5: 0~270, Other(1,2,3,4,6):0~180
    # climp 0:biggest, 180:smallest
    def __init__(self):
        self.Arm = Arm_Device() # Obtain the robotic arm object
        time.sleep(2)
        self.deg = [0, 0, 0, 0, 0, 0]
        self.x, self.y, self.h = 0, 0, 0
        self.observation_pos()

    def call_pos(self):
        all_pos = []
        for i in range(6):
            aa = self.Arm.Arm_serial_servo_read(i+1)
            all_pos.append(aa)
            time.sleep(0.5)
        print(all_pos)
        return all_pos

    def query_pos(self, id):
        return self.deg[id - 1]

    def query_xyh(self):
        return self.x, self.y, self.h

    def query_forward_kinematics(self):
        return forward_kinematics(self.deg[0], self.deg[1], self.deg[2], self.deg[3])

    def start_pos(self):
        self.Arm.Arm_serial_servo_write6(90, 135, 15, 30, 90, 160, 3000)
        self.deg = [90, 135, 15, 30, 90, 160]
        self.x, self.y, self.h = self.query_forward_kinematics()
        time.sleep(3)

    def observation_pos(self):
        self.Arm.Arm_serial_servo_write6(125, 180, 0, 15, 90, 160, 3000)
        self.deg = [125, 180, 0, 15, 90, 160]
        self.x, self.y, self.h = self.query_forward_kinematics()
        time.sleep(3)

    def move_height(self, h, time_lim=600):
        r = math.sqrt(self.x * self.x + self.y * self.y)
        succ, th1, th2, th3 = move_plane_enum_gamma(r, h)
        if(not succ):
            return False
        # Raise the No.2 servo first to prevent sweeping
        if(h > self.h):
            h_deg = min(180, self.deg[1] + 10)
            self.Arm.Arm_serial_servo_write(2, h_deg, 250)
            time.sleep(0.25)
        #print(th1, th2, th3)
        self.deg[1], self.deg[2], self.deg[3] = th1, th2, th3
        self.h = h
        self.Arm.Arm_serial_servo_write6(self.deg[0], self.deg[1],
            self.deg[2], self.deg[3], self.deg[4], self.deg[5], time_lim)
        time.sleep(time_lim/1000)
        return True

    def move_rotate(self, d, time_lim=600):
        th0 = self.deg[0] + d
        if(th0 < 0.1 or th0 > 179.9):
            return False
        self.deg[0] = th0
        self.x, self.y, self.h = self.query_forward_kinematics()
        self.Arm.Arm_serial_servo_write(1, th0, time_lim)
        time.sleep(time_lim / 1000)
        return True

    def move(self, x, y, h, time_lim=2000):
        r = math.sqrt(x * x + y * y)
        #print(x, y, h)
        th0 = math.atan2(y, x) * RA2DE
        if(th0 < 0.1 or th0 > 179.9):
            return False
        succ, th1, th2, th3 = move_plane_enum_gamma(r, h)
        if(not succ):
            return False
        #print(th0, th1, th2, th3)
        self.deg[0], self.deg[1], self.deg[2], self.deg[3] = th0, th1, th2, th3
        self.x, self.y, self.h = x, y, h
        self.Arm.Arm_serial_servo_write6(self.deg[0], self.deg[1],
            self.deg[2], self.deg[3], self.deg[4], self.deg[5], time_lim)
        time.sleep(time_lim / 1000)
        return True