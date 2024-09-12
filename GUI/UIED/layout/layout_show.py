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

import cv2

from GUI.utils import random_color

def visualize(img_path, dataframe, show_method, attr='class'):
    img = cv2.imread(img_path)
    colors = {}
    for i in range(len(dataframe)):
        compo = dataframe.iloc[i]
        if(compo[attr] == -1):
            continue
        else:
            if(compo[attr] not in colors):
                colors[compo[attr]] = random_color()
            if(show_method == 'block'):
                img = cv2.rectangle(img, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max), colors[compo[attr]], -1)
            elif(show_method == 'line'):
                img = cv2.rectangle(img, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max), colors[compo[attr]], 2)
            #img = cv2.putText(img, str(compo[attr]), (compo.column_min + 5, compo.row_min + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    cv2.imshow('layout', cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2))))
    cv2.waitKey(0)
    cv2.destroyWindow('layout')

def visualize_list(img_path, lists, color=(166,100,255), show_method='none'):
    img = cv2.imread(img_path)

    for l in lists:
        l.visualize(img, color, show_method=show_method)

    cv2.imshow('lists', cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2))))
    cv2.waitKey(0)
    cv2.destroyWindow('lists')

def save_lists_img(img, lists, write_path, show_method='block'):
    for l in lists:
        l.visualize(img, color=(166,100,255), show_method=show_method)
    cv2.imwrite(write_path, img)