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

import pandas as pd
import cv2
from os.path import join as pjoin
import time

from GUI.UIED.layout.composDF import ComposDF
from GUI.data_structure.List import List, save_lists_json
import GUI.UIED.layout.repetition_recog as rep
from GUI.UIED.layout.layout_show import visualize, visualize_list, save_lists_img

def cvt_groups_to_list_compos(df):
    lists = []

    # multiple list (multiple compos in each list item)
    groups = df.groupby('group_pair').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(list_class='multi', df=df.loc[groups[i]], list_alignment=df.loc[groups[i][0]]['alignment']))
        # remove selected compos
        df = df.drop(list(groups[i]))

    # single list (single compo in each list item)
    groups = df.groupby('group').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(list_class='single', df=df.loc[groups[i]], list_alignment=df.loc[groups[i][0]]['alignment']))
        # remove selected compos
        df = df.drop(list(groups[i]))

    return lists

# ===============group by clustering================
def layout_clustering(img_path, elements, texts, output_dir):
    start = time.perf_counter()

    # step1: cluster elements into groups according to position and area (group, alignment_in_group)
    elements_cd = ComposDF(img_path, elements, False)
    df_elements = rep.recog_repetition_elements(elements_cd)
 
    texts_cd = ComposDF(img_path, texts, True)
    df_texts = rep.recog_repetition_texts(texts_cd)

    # merge all compos
    df_all = pd.merge(df_elements, df_texts, how='outer')
    for i in range(len(df_all)):
        if(df_all.loc[i, 'group'] != -1):
            k = str(int(df_all.loc[i, 'group']))
            if(df_all.loc[i, 'class'] == 'Text'):
                df_all.loc[i, 'group'] = 't-' + k
            else:
                df_all.loc[i, 'group'] = 'e-' + k

    #df_all.rename({'alignment': 'alignment_in_group'}, axis=1, inplace=True)
    
    all_cd = ComposDF(img_path, df_all, create=False)
    all_cd.regroup_compos_by_compos_gap()
    all_cd.check_group_validity_by_compos_gap()

    # step2: pair clusters (groups) into a larger group (group_pair, pair_to)
    all_cd.pair_groups() 

    # step3: identify list item (paired elements) in each compound large group (list_item)
    all_cd.list_item_partition()

    # step4: filter out invalid unpaired groups
    all_cd.remove_invalid_groups()

    # step5: add missed compos by checking group items
    all_cd.add_missed_compos_by_checking_group_item()
    #visualize(img_path, all_cd.dataframe, 'block', attr='group')

    # step6: convert groups to list compos
    lists = cvt_groups_to_list_compos(all_cd.dataframe)
    #visualize_list(img_path, lists)

    # step7: save results
    img = cv2.imread(img_path)
    name = img_path.replace('\\', '/').split('/')[-1][:-4]
    save_lists_json(pjoin(output_dir, name+'.json'), lists, img.shape)
    save_lists_img(img, lists, pjoin(output_dir, name+'.jpg'))

    print("[Clustering Completed in %.3f s] Output: %s" % (time.perf_counter() - start, pjoin(output_dir, name+'.json')))

    return lists