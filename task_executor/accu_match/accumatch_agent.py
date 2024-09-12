import json
from os.path import join as pjoin
import cv2

from task_executor.accu_match.screen_finder import ScreenFinder
from task_executor.keyboard import keyboard_calc_char, keyboard_calc_enter

def load_steps(path):
    path = pjoin('./asset/instruction_step_file/', path)
    with open(path, 'r') as file:
        return json.load(file)

class AccuMatchAgent:
    def __init__(self, embedding_method='BGEM3', 
        dict_path='./asset/instruction_dict/dict.json'):

        if(embedding_method == 'BGEM3'):
            from task_executor.BGEM3.instruction_match import InsMatch
            self.ins_match = InsMatch(dict_path=dict_path)
        else:
            raise ValueError('Instruction embedding method is not supported:' + str(embedding_method))

        self.screen_finder = ScreenFinder()

        self.app = None
        slef.task = None
        self.now_step = None 

    def set_APPname(self, name):
        self.APPname = name

    def set_task(self, app, task):
        self.task = task
        self.app = app

        similar_instrs = self.ins_match.K_similar(task, self.APPname, K=1)
        self.steps = load_steps(similar_instrs[0])['steps']
        self.round_count = 0

    def str2coord(self, param):
        self.screen_finder.load_screen_texts(screen_detect_dict['text'])
        x, y = self.screen_finder.find_text(param)
        return x, y

    def exe_task(self, step, screen_detect_dict):
        if(self.round_count >= len(self.steps)):
            return {'state':True, 'finish': True}

        new_step = {}
        new_step['function'] = step['function']

        if(step['function'] == 'tap' or step['function'] == 'long_press'):
            x, y = str2coord(self, step['param'])
            new_step['x'] = x
            new_step['y'] = y
        elif(step['function'] == 'scroll'):
            new_step['direction'] = step['param']
        elif(step['function'] == 'text'):
            new_step['input_str'] = step['param']
        elif(step['function'] == 'back'):
            pass

        return {'state':True, 'finish': False, 'step': new_step}