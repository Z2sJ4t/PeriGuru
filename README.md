# PeriGuru - A Peripheral Robotic Mobile App Operation Assistant based on GUI Image Understanding and Prompting with LLM

## Overview

Smartphones have become an integral part of daily life, serving as tools for reading, learning, socializing, and shopping. However, not all users find mobile apps easy to navigate.

Smartphones have significantly enhanced our daily learning, communication, and entertainment, becoming an essential component of modern life. However, certain populations, including the seniors and individuals with visual impairments, encounter challenges in utilizing smartphones, thus necessitating mobile app operation assistants, a.k.a. mobile app agent.

With considerations for privacy, permissions, and cross-platform compatibility issues, we endeavor to devise and develop a peripheral robotic mobile app operation assistant, *PeriGuru*. PeriGuru leverages a suite of computer vision (CV) techniques to analyze GUI screenshot images and employs LLM to inform action decisions, which are then executed by robotic arms.

## Open Source Credits

This project makes use of the following open-source projects, for which we are grateful:

| Name | License | Link |
| --- | ---- | --- |
| AppAgent | MIT license | [https://github.com/mnotgod96/AppAgent](https://github.com/mnotgod96/AppAgent) |
| BGEM3 | MIT license | [https://hf-mirror.com/BAAI/bge-m3/tree/main](https://hf-mirror.com/BAAI/bge-m3/tree/main) |
| GUI-Perceptual-Grouping | Apache-2.0 license | [https://github.dev/MulongXie/GUI-Perceptual-Grouping](https://github.dev/MulongXie/GUI-Perceptual-Grouping) |
| LabelDroid | GPL-3.0 license | [https://github.com/chenjshnn/LabelDroid](https://github.com/chenjshnn/LabelDroid) |
| UIED | Apache-2.0 license | [https://github.com/MulongXie/UIED](https://github.com/MulongXie/UIED) |
| YOLOv5 |  AGPL-3.0 license | [https://github.com/ultralytics/yolov5](https://github.com/ultralytics/yolov5) |

## Installation and Usage Instructions

The code was tested on Ubuntu 20.04, with Python 3.8.10, PyTorch 2.2.1, and torchvision 0.17.1.

1. Clone this repository.

```shell
git clone https://github.com/Z2sJ4t/PeriGuru.git
cd PeriGuru
```

2. Install the requirements.

```shell
pip install -r requirements.txt
```

3. Install third-party repositories.

Please install the third-party repositories and models in the `third_party` folder, which includes [BGEM3](https://hf-mirror.com/BAAI/bge-m3/tree/main), [LabelDroid](https://github.com/chenjshnn/LabelDroid), and [YOLOv5](https://github.com/ultralytics/yolov5).


4. Set your API Key.

Please replace the OpenAI API key at `task_executor/LLM/LLM_agent.py line 8` with your own. If you need to use other LLM models, you can make modifications in `task_executor/LLM/model.py`.

The configuration of OCR model is in `GUI/UIED/text/ocr_method`. You can use the Baidu API usage example provided in `GUI/UIED/text/ocr_method/baidu.py` and replace the API key on line 9 with your own, or write the calling interface for other API key refering to it.


5. Configure your robotic arm.

The robotic arm used in PeriGuru's testing is the [yahboom DOFBOT SE](http://www.yahboom.net/study/DOFBOT_SE). The file for configuring robot motion is `robot_movement/robot.py`. You can modify this file to fit your own robotic arm.

## Folder structure

`camera/`

- Configure the camera and obtain screenshots.

`GUI/`

- Identify UI elements and layout.

`task_executor/`

- Generate action strategies to complete tasks.

`robot_movement/` 

- Guide the movement of the robotic arm and execute actions.

## Demo

![](https://github.com/Z2sJ4t/PeriGuru/blob/main/asset/demo_1.gif)

![](https://github.com/Z2sJ4t/PeriGuru/blob/main/asset/demo_2.gif)