import json
from os.path import join as pjoin
import cv2

from robot_movement.actuator import Actuator
from robot_movement.keyboard import keyboard_calc_char, keyboard_calc_enter

class FuncActor:
    def __init__(self, use_actuator=False):
        self.use_actuator = use_actuator
        if(use_actuator):
            self.actuator = Actuator()

    def exec_step(self, step, screen_detect_dict):
        if(step['function'] == 'tap'):
            if('keyboard_min_x' in screen_detect_dict):
                return False, 'keyboard here'

            x, y = step['x'], step['y']
            print(x, y)
            if(self.use_actuator):
                self.actuator.tap(x, y)
                self.actuator.observation_pos()
            return True, 'sucess'

        elif(step['function'] == 'long_press'):
            if('keyboard_min_x' in screen_detect_dict):
                return False, 'keyboard here'

            x, y = step['x'], step['y']
            print(x, y)
            if(self.use_actuator):
                self.actuator.long_tap(x, y)
                self.actuator.observation_pos()
            return True, 'sucess'

        elif(step['function'] == 'scroll'):
            if('keyboard_min_x' in screen_detect_dict):
                return False, 'keyboard here'

            if(step['direction'] == 'up'):
                self.actuator.scroll_up(0.5, 0.3)
                self.actuator.observation_pos()
                return True, 'sucess'
            if(step['direction'] == 'down'):
                self.actuator.scroll_down(0.5, 0.7)
                self.actuator.observation_pos()
                return True, 'sucess'
            return False, 'direction error'

        elif(step['function'] == 'text'):
            if('keyboard_min_x' not in screen_detect_dict):
                return False, 'no keyboard'
            keyboard_min_x = screen_detect_dict['keyboard_min_x']
            keyboard_min_y = screen_detect_dict['keyboard_min_y']
            keyboard_width = screen_detect_dict['keyboard_width']
            keyboard_height = screen_detect_dict['keyboard_height']
            for char in step['input_str']:
                flag, x, y = keyboard_calc_char(char)
                if(flag):
                    x = keyboard_min_x + keyboard_width * x
                    y = keyboard_min_y + keyboard_height * y
                    if(self.use_actuator):
                        self.actuator.tap(x, y)
            x, y = keyboard_calc_enter()
            x = keyboard_min_x + keyboard_width * x
            y = keyboard_min_y + keyboard_height * y
            if(self.use_actuator):
                self.actuator.tap(x, y)
            return True, 'sucess'

        elif(step['function'] == 'back'):
            back_x, back_y = 0.2, 0.97
            #print(back_x, back_y)
            if(self.use_actuator):
                self.actuator.tap(back_x, back_y)
                self.actuator.observation_pos()
            return True, 'sucess'

        return False, 'function error'

    def position_cacalibration(self, cam, show=False):
        if(self.use_actuator):
            self.actuator.draw_cacalibration_points()
            img = cam.get_screen()
            img_path = './asset/test_image/position.jpg'
            cv2.imwrite(img_path, img)
            self.actuator.get_cacalibration_M(img_path, show=show)

    def observation_pos(self):
        if(self.use_actuator):
            self.actuator.observation_pos()