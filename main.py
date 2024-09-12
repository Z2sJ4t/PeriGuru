import cv2
from os.path import join as pjoin
import time

from camera.camera import Camera
from robot_movement.func_actor import FuncActor
from GUI.gui_detector import GUI_detector
from task_executor.LLM.LLM_agent import LLMAgent

from GUI.LabelDroid.data_utils.Vocabulary import Vocabulary

MAX_LOOP = 15

cam = Camera()
print('Choose 4 points to anchor the screen area.')
cam.anchor() # anchor the screen area

# Start the robot
print('Starting the robot...')
funcActor = FuncActor(use_actuator=False)
print('Successfully started the robot!')

cam.restart_cam()

# Create LLM agent

APP_name = input("Enter APP name: ")
gui_detector = GUI_detector()
agent = LLMAgent('OpenAI', './output/task_log', use_img=True)

funcActor.observation_pos()

task_cnt = 0

while(True):
    task = input('Enter new task: ')
    if(task == 'exit'):
        break

    # set task
    agent.set_task(APP_name, task)
    
    round_count = 0
    error_report = ''
    output_dir = './output/'

    # task cycle
    while(True):
        frame = cam.get_screen()
        img_path = pjoin(pjoin(output_dir, 'screen_shoot'), str(round_count)+'.jpg')
        cv2.imwrite(img_path, frame)

        if(round_count >= MAX_LOOP):
            print('Exceeded the maximum loop number.')
            break

        keyboard_flag, keyboard_min_x, keyboard_min_y, keyboard_width, keyboard_height = \
            gui_detector.detect_keyboard(img_path)
        if(keyboard_flag):
            screen_detect_dict = {
                'keyboard_min_x': keyboard_min_x,
                'keyboard_min_y': keyboard_min_y,
                'keyboard_width': keyboard_width,
                'keyboard_height': keyboard_height
            }
            act_step = agent.exe_task(str(task_cnt), round_count, None, img_path, {}, error_report)
        else:
            ele_list, html_res = gui_detector.detect(img_path)
            screen_detect_dict = ele_list
            act_step = agent.exe_task(str(task_cnt), round_count, html_res, img_path, ele_list, error_report)

        if(act_step['finish']):
            print('Task finished!')
            break
        if(not act_step['state']):
            continue

        # execution
        _, actor_res = funcActor.exec_step(act_step['step'], screen_detect_dict)
        if(actor_res == 'no keyboard'):
            error_report = 'Previous error report: There is no keyboard on the current interface, please do not call the Text() function.'
        elif(actor_res == 'keyboard here'):
            error_report = 'Previous error report: There is a keyboard on the current interface. Before performing other operations, please call the back() function to close the keyboard.'
        else:
            error_report = ''

        round_count += 1
        time.sleep(0.2)

    task_cnt += 1

cam.release_cam()