import numpy as np
import cv2
import json
import time
import re
from os.path import join as pjoin

from GUI.data_structure.Text import Text
from GUI.data_structure.Text import save_texts_json, load_texts_json

def visualize_texts(org_img, texts, shown_resize_height=None, write_path=None):
    img = org_img.copy()
    for text in texts:
        text.visualization(img, line=2)
    
    img_resize = img
    if shown_resize_height is not None:
        img_resize = cv2.resize(img, (int(shown_resize_height * (img.shape[1]/img.shape[0])), shown_resize_height))
    if write_path is not None:
        cv2.imwrite(write_path, img_resize)

def text_filter_noise(texts, en_only=True):
    valid_texts = []
    en_pattern = re.compile('[^\u0041-\u007A\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF]+')
    for text in texts:
        # Remove non ascii
        if(en_only):
            text.words = re.sub(r'[^\x00-\x7F]+', '', text.words)
        if(len(text.words) < 3):
            continue
        #if(text.cal_height() / img_shape[0] < 0.015):
        #    continue
        valid_texts.append(text)
    return valid_texts

# If two paragraphs of text have high overlap on x-axis, similar heights,
#  close distances on y-axis, and are alignment, they are considered to be merged together.
def merge_line_breaks(texts):
    valid_texts = []
    HEIGHT_RATIO = 0.8
    HEIGHT_CLOSE = 0.55
    X_OVERLAP = 0.85

    for text1 in texts:
        flag = True
        for i in range(len(valid_texts)):
            text2 = valid_texts[i]
            min_w = min(text1.cal_width(), text2.cal_width())
            max_w = max(text1.cal_width(), text2.cal_width())
            overlap = text1.x_overlap(text2)
            if(overlap / min_w < X_OVERLAP): # overlap on x-axis
                continue
            min_sh = min(text1.singel_height, text2.singel_height)
            max_sh = max(text1.singel_height, text2.singel_height)
            if(min_sh / max_sh < HEIGHT_RATIO): # similar heights
                continue
            dist = text1.y_distance(text2)
            if(dist / min_sh > HEIGHT_CLOSE): # close on y-axis
                continue
            if(not text1.is_alignment_vertical(text2)): # alignment
                continue

            valid_texts[i].merge(text1)
            flag = False

        if(flag):
            valid_texts.append(text1)

    return valid_texts

def text_detection(img_path, output_dir, method='baidu'):
    start = time.perf_counter()
    name = img_path.replace('\\', '/').split('/')[-1][:-4]
    img = cv2.imread(img_path)

    if(method=='baidu'):
        import GUI.UIED.text.ocr_method.baidu as ocr
        #texts = load_texts_json(pjoin(output_dir, name+'.json'))
        texts = ocr.ocr_detection(img_path)
        save_texts_json(pjoin(output_dir, name+'_origin.json'), texts, img.shape)
        texts = merge_line_breaks(texts)
        texts = text_filter_noise(texts)
    else:
        raise ValueError('OCR method is not supported:' + str(method))

    visualize_texts(img, texts, write_path=pjoin(output_dir, name+'.jpg'))
    save_texts_json(pjoin(output_dir, name+'.json'), texts, img.shape)
    print("[Text Detection Completed in %.3f s] Input: %s Output: %s" % (time.perf_counter() - start, img_path, pjoin(output_dir, name+'.json')))
    
    return texts