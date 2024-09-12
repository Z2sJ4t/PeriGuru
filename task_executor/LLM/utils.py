import base64
import cv2
import pyshine as ps
import os
from colorama import Fore, Style

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def draw_bbox_multi(img_path, output_path, elem_list, dark_mode=False):
    image = cv2.imread(img_path)
    height, width, _ = image.shape

    count = 1
    for e_id, e in elem_list.items():
        if(e['cls'] == 'Image' or e['cls'] == 'Icon' or e['cls'] == 'CheckedTextView'):
            left, top = e['left'], e['top']
            right, bottom = e['right'], e['bottom']

            label = str(e_id)

            text_color = (10, 10, 10) if dark_mode else (255, 250, 250)
            bg_color = (255, 250, 250) if dark_mode else (10, 10, 10)
            #image = ps.putBText(image, label, text_offset_x=(left + right) // 2 + 10, text_offset_y=(top + bottom) // 2 + 10,
            #                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=bg_color,
            #                    text_RGB=text_color, alpha=0.5)
            image = ps.putBText(image, label, text_offset_x=(left + right) // 2 + 4, text_offset_y=(top + bottom) // 2 + 4,
                                vspace=4, hspace=4, font_scale=0.8, thickness=1, background_RGB=bg_color,
                                text_RGB=text_color, alpha=0.5)

    cv2.imwrite(output_path, image)
    return width, height