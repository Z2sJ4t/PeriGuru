import cv2

class Compo:
    def __init__(self, location):
        self.location = location
        self.id = -1

    def set_id(self, id):
        self.id = id

    def cal_area(self):
        return (self.location['right'] - self.location['left']) * (self.location['bottom'] - self.location['top'])

    def cal_width(self):
        return self.location['right'] - self.location['left']
    
    def cal_height(self):
        return self.location['bottom'] - self.location['top']

    def visualization(self, img, color=(0, 0, 255), line=1):
        loc = self.location
        cv2.rectangle(img, (loc['left'], loc['top']), (loc['right'], loc['bottom']), color, line)

    def x_overlap(self, compo):
        if(self.location['left'] < compo.location['left']):
            overlap = self.location['right'] - compo.location['left']
            return max(0, overlap)
        else:
            overlap = compo.location['right'] - self.location['left']
            return max(0, overlap)

    def y_overlap(self, compo):
        if(self.location['top'] < compo.location['top']):
            overlap = self.location['bottom'] - compo.location['top']
            return max(0, overlap)
        else:
            overlap = compo.location['bottom'] - self.location['top']
            return max(0, overlap)

    def x_distance(self, compo):
        if(self.location['left'] > compo.location['left']):
            dist = self.location['left'] - compo.location['right']
            return max(0, dist)
        else:
            dist = compo.location['left'] - self.location['right']
            return max(0, dist)

    def y_distance(self, compo):
        if(self.location['top'] > compo.location['top']):
            dist = self.location['top'] - compo.location['bottom']
            return max(0, dist)
        else:
            dist = compo.location['top'] - self.location['bottom']
            return max(0, dist)

    def iou(self, compo):
        min_x = max(self.location['left'], compo.location['left'])
        min_y = max(self.location['top'], compo.location['top'])
        max_x = min(self.location['right'], compo.location['right'])
        max_y = min(self.location['bottom'], compo.location['bottom'])
        w = max(0, max_x - min_x)
        h = max(0, max_y - min_y)

        area_a = self.cal_area()
        area_b = compo.cal_area()
        inter = w * h

        iou = inter / (area_a + area_b - inter)
        ioa = inter / area_a
        iob = inter / area_b

        return iou, ioa, iob

    def is_alignment_vertical(self, compo, threshold=0.1):
        width = min(self.cal_width(), compo.cal_width())
        if(abs(self.location['left'] - compo.location['left']) / width < threshold):
            return True
        if(abs(self.location['right'] - compo.location['right']) / width < threshold):
            return True
        c1 = (self.location['right'] + self.location['left']) / 2
        c2 = (compo.location['right'] + compo.location['left']) / 2
        if(abs(c1 - c2) / width < threshold):
            return True
        return False

    def is_alignment_level(self, compo, threshold=0.1):
        height = min(self.cal_height(), compo.cal_height())
        if(abs(self.location['top'] - compo.location['top']) / height < threshold):
            return True
        if(abs(self.location['bottom'] - compo.location['bottom']) / height < threshold):
            return True
        c1 = (self.location['top'] + self.location['bottom']) / 2
        c2 = (compo.location['top'] + compo.location['bottom']) / 2
        if(abs(c1 - c2) / height < threshold):
            return True
        return False
