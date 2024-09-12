import json
from os.path import join as pjoin
from functools import cmp_to_key

from GUI.data_structure.Compo import Compo

def load_dfs(data):
    loc = {'left': data['column_min'], 'top': data['row_min'], 
            'right': data['column_max'], 'bottom': data['row_max']}
    
    if(data['cls'] == 'Text' or data['cls'] == 'Icon'):
        if('text' in data):
            return LayoutP(data['cls'], data['id'], data['text'], loc)
        else:
            return LayoutP(data['cls'], data['id'], None, loc)

    item_div = LayoutDiv(data['cls'], data['id'], loc)
    for c in data['child']:
        item_div.child.append(load_dfs(c))
    return item_div
    
def load_layout_json(file_dir, name):
    with open(pjoin(file_dir, name + '.txt'), 'r', encoding='utf-8') as f:
        html_res = f.read()
    with open(pjoin(file_dir, name + '.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
        image_shape = data['img_shape']
        layout = Layout()
        for c in data['items']:
            layout.layout_items.append(load_dfs(c))
    return layout, html_res, image_shape

def sort_layout_compo(x, y):
    if(x.location['bottom'] <= y.location['top']):
        return -1
    if(x.location['top'] >= y.location['bottom']):
        return 1
    if(x.location['right'] <= y.location['left']):
        return -1
    if(x.location['left'] >= y.location['right']):
        return 1
    cnt = 0
    if(x.location['left'] < y.location['left']):
        cnt += 1
    if(x.location['right'] < y.location['right']):
        cnt += 1
    if(x.location['top'] < y.location['top']):
        cnt += 1
    if(x.location['bottom'] < y.location['bottom']):
        cnt += 1
    if(cnt > 2):
        return -1
    if(cnt < 2):
        return 1
    return 0

# List, ListItem, Image, CheckedTextView, EditText
class LayoutDiv(Compo):
    def __init__(self, cls, id, location):
        super().__init__(location)
        self.cls = cls
        self.id = id
        self.child = []

    def re_numbering(self, ids):
        self.id = ids
        ids += 1
        for c in self.child:
            ids = c.re_numbering(ids)
        return ids

    def generate_html(self, dep):
        res = ' ' * dep
        res += '<div id=' + str(self.id) + ' class="' + self.cls + '">\n'
        for c in self.child:
            res += c.generate_html(dep + 1)
        res += ' ' * dep
        res += '</div>\n'
        return res

    def generate_json(self):
        res = {'cls': self.cls, 'id': self.id}
        loc = self.location
        res['column_min'], res['row_min'], res['column_max'], res['row_max'] = \
            loc['left'], loc['top'], loc['right'], loc['bottom']
        res['child'] = []
        for c in self.child:
            res['child'].append(c.generate_json())
        return res

    def generate_ele_list(self, ele_list):
        ele = {
            'cls': self.cls,
            'left': self.location['left'],
            'right': self.location['right'],
            'top': self.location['top'],
            'bottom': self.location['bottom']
        }
        ele_list[self.id] = ele
        for c in self.child:
            c.generate_ele_list(ele_list)

    def include(self, p):
        iou, ioa, iob = super().iou(p)
        if(iob < 0.8):
            return False

        for c in self.child:
            if(c.include(p)):
                return True
        self.child.append(p)
        return True

    def sort(self):
        self.child.sort(key=cmp_to_key(sort_layout_compo))
        for c in self.child:
            c.sort()

# Icon, Text
class LayoutP(Compo):
    def __init__(self, cls, id, text, location):
        super().__init__(location)
        self.cls = cls
        self.id = id
        self.text = text

    def re_numbering(self, ids):
        self.id = ids
        return ids + 1

    def generate_html(self, dep):
        res = ' ' * dep
        res += '<p id=' + str(self.id) + ' class="' + self.cls + '">'
        if(self.text is not None):
            res += self.text
        res += '</p>\n'
        return res

    def generate_json(self):
        res = {'cls': self.cls, 'id': self.id}
        if(self.text is not None):
            res['text'] = self.text
        loc = self.location
        res['column_min'], res['row_min'], res['column_max'], res['row_max'] = \
            loc['left'], loc['top'], loc['right'], loc['bottom']
        return res

    def generate_ele_list(self, ele_list):
        ele = {
            'cls': self.cls,
            'left': self.location['left'],
            'right': self.location['right'],
            'top': self.location['top'],
            'bottom': self.location['bottom']
        }
        ele_list[self.id] = ele

    def include(self, p):
        return False
    
    def sort(self):
        return

class Layout:
    def __init__(self):
        self.upper_task_bar = []
        self.drawer = []
        self.background_image = []
        self.modal = []
        self.page_indicator = []

        self.layout_items = []

    def check_unable(self, compo):
        for x in self.upper_task_bar:
            iou, ioa, iob = compo.iou(x)
            if(ioa > 0.9):
                return True
        for x in self.drawer:
            iou, ioa, iob = compo.iou(x)
            if(ioa < 0.9):
                return True
        for x in self.modal:
            iou, ioa, iob = compo.iou(x)
            if(ioa < 0.9):
                return True
        return False

    def re_numbering(self):
        ids = 1
        for item in self.layout_items:
            ids = item.re_numbering(ids)

    def generate_html(self):
        res = ''
        for item in self.layout_items:
            res += item.generate_html(0)
        return res

    def generate_json(self, file_path, img_shape):
        f_out = open(file_path, 'w', encoding='utf-8')
        output = {'img_shape': img_shape, 'items': []}
        for x in self.layout_items:
            output['items'].append(x.generate_json())
        json.dump(output, f_out, indent=4, ensure_ascii=False)

    def generate_ele_list(self):
        ele_list = {}
        for x in self.layout_items:
            x.generate_ele_list(ele_list)
        return ele_list

    def hierarchical(self):
        new_items = []
        for i in range(len(self.layout_items)):
            x = self.layout_items[i]
            flag = True
            for j in range(len(self.layout_items)):
                if(i == j):
                    continue
                y = self.layout_items[j]
                if(y.include(x)):
                    flag = False
                    break
            if(flag):
                new_items.append(x)
        self.layout_items = new_items

        for x in self.layout_items:
            x.sort()
        self.layout_items.sort(key=cmp_to_key(sort_layout_compo))