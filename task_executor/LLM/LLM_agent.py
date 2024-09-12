import re
import json
import time
import os
import cv2

import task_executor.LLM.prompts as prompts
from task_executor.LLM.utils import draw_bbox_multi
from task_executor.LLM.model import OpenAIModelwithImg, OpenAIModelnoImg, parse_rsp

MAX_ROUND = 12

class LLMAgent:
    def __init__(self, model, output_dir, use_img=False):
        if(model == 'OpenAI'):
            # ! Add your API Key here
            if(use_img):
                BASE_URL = 
                API_KEY = 
                MODEL = 
                self.mllm = OpenAIModelwithImg(BASE_URL, API_KEY, MODEL)
            else:
                BASE_URL = 
                API_KEY = 
                MODEL = 
                self.mllm = OpenAIModelnoImg(BASE_URL, API_KEY, MODEL)
        self.task = None
        self.app = None
        self.output_dir = output_dir
        self.action_record = []
        self.use_img = use_img

    def set_task(self, app, task):
        self.task = task
        self.app = app
        self.action_record = []

    def previous_actions(self):
        if(len(self.action_record) == 0):
            return 'None'
        res = ''
        for i, action in enumerate(self.action_record):
            res += str(i+1) + '. '
            res += action
            res += ' '
        return res

    def exe_task(self, log_name, round_count, html_doc, img_path, ele_list, error_report=''):
        start = time.perf_counter()

        log_path = os.path.join(self.output_dir, f"{log_name}.json")

        if(round_count > MAX_ROUND):
            return {'state':False, 'finish': False}

        if(self.use_img): # label the image
            prompt = prompts.task_template_img
            img_path_new = os.path.join(self.output_dir, f"{log_name}_{round_count}_labeled.jpg")
            width, height = draw_bbox_multi(img_path, img_path_new, ele_list)
        else:
            prompt = prompts.task_template
            image = cv2.imread(img_path)
            height, width, _ = image.shape
            img_path_new = os.path.join(self.output_dir, f"{log_name}_{round_count}.jpg")

        prompt = re.sub(r"<APP_name>", self.app, prompt)
        prompt = re.sub(r"<task_description>", self.task, prompt)
        prompt = re.sub(r"<last_acts>", self.previous_actions(), prompt)
        prompt = re.sub(r"<error_report>", error_report, prompt)

        if(html_doc is None): # keyboard
            prompt = re.sub(r"<keyboard_text>", prompts.keyboard_text, prompt)
            prompt = re.sub(r"<keyboard_other>", prompts.keyboard_other, prompt)
            prompt = re.sub(r"<keyboard_back>", prompts.keyboard_back, prompt)
            html_doc = '<div id=1 class="Keyboard"></div>'
            prompt = re.sub(r"<screen_description>", html_doc, prompt)
        else:
            prompt = re.sub(r"<keyboard_text>", prompts.nokeyboard_text, prompt)
            prompt = re.sub(r"<keyboard_other>", "", prompt)
            prompt = re.sub(r"<keyboard_back>", prompts.nokeyboard_back, prompt)
            prompt = re.sub(r"<screen_description>", html_doc, prompt)

        _, rsp = self.mllm.get_model_response(prompt, [img_path_new])

        with open(log_path, "a") as logfile:
            log_item = {"step": round_count, "prompt": prompt, "image": img_path_new,
                        "response": rsp}
            logfile.write(json.dumps(log_item, indent=4) + "\n")

        res = parse_rsp(rsp)

        if(res[0] == "FINISH"):
            return {'state':True, 'finish': True}
        if(res[0] == "ERROR"):
            return {'state':False, 'finish': False}
        
        func_name = res[0]
        act = res[-1]
        self.action_record.append(act)

        step = {}
        step["function"] = func_name

        if(func_name == "tap"):
            if(res[1] not in ele_list):
                return {'state':False, 'finish': False}
            e = ele_list[res[1]]
            left, top = e['left'], e['top']
            right, bottom = e['right'], e['bottom']
            x = (left + right) / 2 / width
            y = (top + bottom) / 2 / height
            step['x'] = x
            step['y'] = y
        elif(func_name == "scroll"):
            step['direction'] = res[1]
        elif(func_name == "text"):
            step['input_str'] = res[1]
        elif(func_name == "back"):
            pass

        print("[Decision making Completed in %.3f s] Output: %s" % (time.perf_counter() - start, log_path))

        return {'state':True, 'finish': False, 'step': step}