"""
   Copyright [2021] [UIED mulong.xie@anu.edu.au]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import time
import cv2
from os.path import join as pjoin

from GUI.data_structure.Layout import Layout, LayoutDiv, LayoutP
from GUI.LabelDroid.icon_description import icon_description

def clean_and_build_layout(elements, texts):
    layout = Layout()
    for i in range(len(elements)-1, -1, -1):
        ele = elements[i]
        if(ele.cls == 'Modal'):
            layout.modal.append(ele)
        elif(ele.cls == 'Drawer'):
            layout.drawer.append(ele)
        elif(ele.cls == 'PageIndicator'):
            layout.page_indicator.append(ele)
        elif(ele.cls == 'BackgroundImage'):
            layout.background_image.append(ele)
        elif(ele.cls == 'UpperTaskBar'):
            layout.upper_task_bar.append(ele)
        else:
            continue
        elements.pop(i)

    for i in range(len(elements)-1, -1, -1):
        if(layout.check_unable(elements[i])):
            elements.pop(i)

    # Delete duplicate detected elements
    for i in range(len(elements)-1, -1, -1):
        e1 = elements[i]
        flag = True
        for j in range(len(elements)):
            if(i == j):
                continue
            e2 = elements[j]
            iou, ioa, iob = e1.iou(e2)
            if(iou > 0.9 and e1.conf < e2.conf):
                flag = False
                break
        if(not flag):
            elements.pop(i)
    
    for i in range(len(texts)-1, -1, -1):
        if(layout.check_unable(texts[i])):
            texts.pop(i)

    ids = 0
    for e in elements:
        e.set_id(ids)
        ids += 1
    for t in texts:
        t.set_id(ids)
        ids += 1

    return layout

def recognize_layout(img_path, layout, elements, texts, lists, output_dir):
    start = time.perf_counter()

    # step1: Convert all elements to a unified format
    ids = len(elements) + len(texts)
    for l in lists:
        list_div, ids = l.build_layout_div(ids, elements)
        layout.layout_items.append(list_div)
        
    img = cv2.imread(img_path)
    img_shape = img.shape
    icons = []
    icons_pic = []
    for e in elements:
        # discribe icons
        if(e.cls == 'Icon'):
            l, r, t, b = e.location['left'], e.location['right'], e.location['top'], e.location['bottom']
            if(r >= img_shape[1]):
                r = img_shape[1] - 1
            if(b >= img_shape[0]):
                b = img_shape[0] - 1
            roi = img[t:b+1, l:r+1]
            roi_deep_copy = roi.copy()
            icons_pic.append(roi_deep_copy)
            icons.append((e.id, e.location))
        else:
            item_div = LayoutDiv(e.cls, e.id, e.location)
            layout.layout_items.append(item_div)

    icon_texts = icon_description(icons_pic)

    for i in range(len(icons)):
        #print(icon_texts[i])
        if(icon_texts[i] != '<unk>'): 
            item_p = LayoutP('Icon', icons[i][0], icon_texts[i], icons[i][1])
        else:
            item_p = LayoutP('Icon', icons[i][0], None, icons[i][1])
        layout.layout_items.append(item_p)

    for t in texts:
        item_p = LayoutP('Text', t.id, t.words, t.location)
        layout.layout_items.append(item_p)

    for e in layout.modal:
        layout.layout_items.append(LayoutDiv(e.cls, ids, e.location))
        ids += 1
    
    for e in layout.drawer:
        layout.layout_items.append(LayoutDiv(e.cls, ids, e.location))
        ids += 1
    
    for e in layout.page_indicator:
        layout.layout_items.append(LayoutP(e.cls, ids, None, e.location))
        ids += 1

    # step2: Establishing hierarchical relationships
    layout.hierarchical()

    # step3: Renumbering, Output and Save
    layout.re_numbering()

    name = img_path.replace('\\', '/').split('/')[-1][:-4]

    html_res = layout.generate_html()
    with open(pjoin(output_dir, name + '.txt'), 'w') as file:
        file.write(html_res)
    layout.generate_json(pjoin(output_dir, name + '.json'), img_shape)

    print("[Layout Recognization Completed in %.3f s]" % (time.perf_counter() - start))
    return layout, html_res