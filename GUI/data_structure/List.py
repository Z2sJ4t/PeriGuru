from collections import Counter
import json
import cv2

from GUI.data_structure.Compo import Compo
from GUI.data_structure.Layout import LayoutDiv, LayoutP
from GUI.utils import draw_label, random_color

def save_lists_json(file_path, lists, img_shape):
    f_out = open(file_path, 'w', encoding='utf-8')
    output = {'img_shape': img_shape, 'lists': []}
    for l in lists:
        c = {'alignment': str(l.list_alignment)}
        loc = l.location
        c['column_min'], c['row_min'], c['column_max'], c['row_max'] = \
            int(loc['left']), int(loc['top']), int(loc['right']), int(loc['bottom'])
        c['list_items'] = []
        for list_item in l.list_items:
            ii = []
            for item in list_item:
                i = {'cls': str(item.cls), 'id': int(item.id)}
                loc = item.location
                i['column_min'], i['row_min'], i['column_max'], i['row_max'] = \
                    int(loc['left']), int(loc['top']), int(loc['right']), int(loc['bottom'])
                ii.append(i)
            c['list_items'].append(ii)
        output['lists'].append(c)
    json.dump(output, f_out, indent=4, ensure_ascii=False)

def load_lists_json(file_path):
    lists = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        image_shape = data['img_shape']
        for c in data['lists']:
            list_items = []
            for ii in c['list_items']:
                list_item = []
                for i in ii:
                    line = {'column_min': i['column_min'], 'row_min': i['row_min'], 
                        'column_max': i['column_max'], 'row_max': i['row_max'],
                        'class': i['cls'], 'id': i['id']}
                    item = ListItem(line)
                    list_item.append(item)
                list_items.append(list_item)
            l = List('load', list_items, c['alignment'])
            lists.append(l)
    return lists, image_shape

class ListItem(Compo):
    def __init__(self, line):
        location = {
            'left': int(line['column_min']),
            'right': int(line['column_max']),
            'top': int(line['row_min']),
            'bottom': int(line['row_max'])
        }
        super().__init__(location)
        self.cls = str(line['class'])
        self.id = int(line['id'])

class List:
    def __init__(self, list_class, df, list_alignment):
        self.list_alignment = str(list_alignment)
        self.list_items = []
        self.item_location = []

        if(list_class == 'load'):
            self.list_items = df
        else:
            self.get_items(list_class, df)
            self.sort_items()
        
        self.cal_location()

    def sort_items(self):
        if self.list_alignment == 'v':
            self.list_items = sorted(self.list_items, key=lambda x: x[0].location['top'])
        else:
            self.list_items = sorted(self.list_items, key=lambda x: x[0].location['left'])

    def get_items(self, list_class, df):
        if(list_class == 'multi'):
            groups = df.groupby('list_item').groups
            for i in groups:
                group = list(groups[i])
                item_compos_df = df.loc[group]
                list_item = []
                for j in range(len(item_compos_df)):
                    item = ListItem(item_compos_df.iloc[j])
                    list_item.append(item)
                self.list_items.append(list_item)
        elif(list_class == 'single'):
            for i in range(len(df)):
                item = ListItem(df.iloc[i])
                self.list_items.append([item])

    def cal_location(self):
        all_loc = self.list_items[0][0].location.copy()

        for list_item in self.list_items:

            loc = list_item[0].location.copy()
            for item in list_item:
                loc['left'] = min(loc['left'], item.location['left'])
                loc['right'] = max(loc['right'], item.location['right'])
                loc['top'] = min(loc['top'], item.location['top'])
                loc['bottom'] = max(loc['bottom'], item.location['bottom'])

            self.item_location.append(loc)
            all_loc['left'] = min(all_loc['left'], loc['left'])
            all_loc['right'] = max(all_loc['right'], loc['right'])
            all_loc['top'] = min(all_loc['top'], loc['top'])
            all_loc['bottom'] = max(all_loc['bottom'], loc['bottom'])

        self.location = all_loc

    def correcting_class(self):
        pair_num = len(self.list_items[0])
        for i in range(pair_num):
            if(self.list_items[0][i].cls == 'Text'):
                continue
            cls_count = []
            for list_item in self.list_items:
                cls_count.append(list_item[i].cls)
            counter = Counter(cls_count)
            unified_cls = max(counter.elements(), key=counter.get)
            for list_item in self.list_items:
                list_item[i].cls = unified_cls

    def visualize(self, img, color=(166,100,255), show_method='none'):
        draw_label(img, self.location, color=color, text='list')
        if(show_method == 'none'):
            return
        for list_item in self.list_items:
            l_color = random_color()
            for item in list_item:
                l, r, t, b = item.location['left'], item.location['right'], item.location['top'], item.location['bottom']
                if(show_method == 'block'):
                    img = cv2.rectangle(img, (int(l), int(t)), (int(r), int(b)), l_color, -1)
                elif(show_method == 'line'):
                    img = cv2.rectangle(img, (int(l), int(t)), (int(r), int(b)), l_color, 2)

    def build_layout_div(self, ids, elements):
        list_div = LayoutDiv('List', ids, self.location)
        ids += 1

        ele_max = len(elements)

        for i in range(len(self.item_location)):
            item_div = LayoutDiv('ListItem', ids, self.item_location[i])
            ids += 1

            list_item = self.list_items[i]
            for item in list_item:
                if(item.id < ele_max):
                    # Class correction
                    elements[item.id].cls = item.cls

            list_div.child.append(item_div)

        return list_div, ids