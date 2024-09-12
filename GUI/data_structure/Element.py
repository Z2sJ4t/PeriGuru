import cv2
import numpy as np
import json

from GUI.data_structure.Compo import Compo

def save_elements_json(file_path, elements, img_shape):
    f_out = open(file_path, 'w', encoding='utf-8')
    output = {'img_shape': img_shape, 'elements': []}
    for ele in elements:
        c = {'conf': ele.conf, 'cls': ele.cls}
        loc = ele.location
        c['column_min'], c['row_min'], c['column_max'], c['row_max'] = loc['left'], loc['top'], loc['right'], loc['bottom']
        output['elements'].append(c)
    json.dump(output, f_out, indent=4, ensure_ascii=False)

def load_elements_json(file_path):
    elements = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        image_shape = data['img_shape']
        for c in data['elements']:
            loc = {'left': c['column_min'], 'top': c['row_min'], 
                'right': c['column_max'], 'bottom': c['row_max']}
            ele = Element(c['cls'], c['conf'], loc)
            elements.append(ele)
    return elements, image_shape

class Element(Compo):
    def __init__(self, cls, conf, location):
        super().__init__(location)
        self.cls = cls
        self.conf = conf
        self.text = []