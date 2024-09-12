import cv2
import numpy as np
import json

from GUI.data_structure.Compo import Compo

def save_texts_json(file_path, texts, img_shape):
    f_out = open(file_path, 'w', encoding='utf-8')
    output = {'img_shape': img_shape, 'texts': []}
    for text in texts:
        c = {'words': text.words}
        loc = text.location
        c['column_min'], c['row_min'], c['column_max'], c['row_max'] = loc['left'], loc['top'], loc['right'], loc['bottom']
        c['singel_height'] = text.singel_height
        c['lines'] = text.lines
        output['texts'].append(c)
    # ensure_ascii=False: do not escape Chinese characters
    json.dump(output, f_out, indent=4, ensure_ascii=False)

def load_texts_json(file_path):
    texts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        image_shape = data['img_shape']
        for c in data['texts']:
            loc = {'left': c['column_min'], 'top': c['row_min'], 
                'right': c['column_max'], 'bottom': c['row_max']}
            text = Text(c['words'], loc)
            text.singel_height = c['singel_height']
            text.lines = c['lines']
            texts.append(text)
    return texts, image_shape

class Text(Compo):
    def __init__(self, words, location):
        super().__init__(location)
        self.words = words

        # height of a singel line
        self.singel_height = location['bottom'] - location['top']
        self.lines = 1
        self.tot_height = location['bottom'] - location['top']

    def merge(self, text):
        if(self.location['top'] < text.location['top']):
            self.words = self.words + ' ' + text.words
            self.location['bottom'] = text.location['bottom']
        else:
            self.words = text.words + ' ' + self.words
            self.location['top'] = text.location['top']
        self.lines += 1
        self.tot_height += text.tot_height
        self.singel_height = self.tot_height / self.lines
        self.location['left'] = min(self.location['left'], text.location['left'])
        self.location['right'] = max(self.location['right'], text.location['right'])