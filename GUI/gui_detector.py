import cv2
import json
from os.path import join as pjoin
import numpy as np

from GUI.data_structure.Text import load_texts_json
from GUI.data_structure.Element import load_elements_json
from GUI.data_structure.List import load_lists_json
from GUI.data_structure.Layout import load_layout_json

def masking(input_path, output_path, elements, color=(231, 124, 129)):
    img = cv2.imread(input_path)
    for e in elements:
        l, r, t, b = e.location['left'], e.location['right'], e.location['top'], e.location['bottom']
        if(r >= img.shape[1]):
            r = img.shape[1] - 1
        if(b >= img.shape[0]):
            b = img.shape[0] - 1
        if(e.cls == 'Modal' or e.cls == 'Drawer'):
            mask = np.full(img.shape, color, dtype=np.uint8)
            mask[t:b+1, l:r+1] = img[t:b+1, l:r+1]
            img = mask
        elif(e.cls == 'Icon' or e.cls == 'Image' or e.cls == 'UpperTaskBar'):
            mask = np.full((b-t+1, r-l+1, 3), color, dtype=np.uint8)
            img[t:b+1, l:r+1] = mask
    cv2.imwrite(output_path, img)

class GUI_detector:
    def __init__(self, method='yolov5', ocr_mode='baidu', output_dir='output'):
        self.method = method
        self.output_dir = output_dir

        self.ocr_mode = ocr_mode
        self.ocr_dir = pjoin(self.output_dir, 'ocr') if output_dir is not None else None
        self.ele_dir = pjoin(self.output_dir, 'compo') if output_dir is not None else None
        self.layout_dir = pjoin(self.output_dir, 'layout') if output_dir is not None else None
        self.clus_dir = pjoin(self.output_dir, 'list') if output_dir is not None else None

    # 1200 x 1920(750)
    def detect_keyboard(self, img_path, threshold=0.35, show=False):
        kt_img = cv2.imread('./asset/keyboard_template.png')
        kt_height, kt_width = kt_img.shape[0], kt_img.shape[1]

        img = cv2.imread(img_path)
        height, width = img.shape[0], img.shape[1]

        #cut_img = img[height - int(kt_height * width / kt_width): height,: , :]

        # height * 1200 * kt_height / 1920 / width
        target_width = width
        target_height = int(height * target_width / width * kt_height / 1920)
        #print(target_width, target_height)
        template = cv2.resize(kt_img, (target_width, target_height))
        #img2 = cv2.resize(cut_img, (target_width, target_height))

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        
        # Obtain locations where matching results exceed the threshold
        similary = float(max(res))
        max_index = np.argmax(res)
        pt = (max_index % res.shape[1], max_index // res.shape[1])
        
        #print('similary:', similary)
        if(similary >= threshold):
            if(show):
                # Draw a rectangular box based on its position
                cv2.rectangle(img, pt, (pt[0] + template.shape[1], pt[1] + template.shape[0]), (0, 255, 0), 2)

                # Display Image
                cv2.namedWindow("Matched Area", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Matched Area", 960, 720)
                cv2.imshow('Matched Area', template)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            # x_min, y_min, x_height, y_height
            return True, pt[0] / width, pt[1] / height, \
                template.shape[1] / width, template.shape[0] / height

        return False, -1, -1, -1, -1
        #similary = ORB_siml(img1, img2)

    def detect(self, img_path, masking_nontext=True, is_ele=True,
        is_ocr=True, is_clus=True, is_layout=True):
        import GUI.UIED.text.text_detection as text
        import GUI.yolov5.element_detection as element
        import GUI.UIED.layout.layout_recognition as lay
        import GUI.UIED.layout.layout_clustering as clus

        name = img_path.replace('\\', '/').split('/')[-1][:-4]

        if(is_ele):
            elements = element.element_detection(img_path, self.ele_dir)
        else:
            elements, _ = load_elements_json(pjoin(self.ele_dir, name + '.json'))

        if(masking_nontext):
            # Masking non-text elements to prevent wrong ocr detection
            ocr_img_path = pjoin(self.layout_dir, name + '.jpg')
            masking(img_path, ocr_img_path, elements)
        else:
            ocr_img_path = img_path

        if(is_ocr):
            texts = text.text_detection(ocr_img_path, self.ocr_dir, method=self.ocr_mode)
        else:
            texts, _ = load_texts_json(pjoin(self.ocr_dir, name + '.json'))

        layout = lay.clean_and_build_layout(elements, texts)

        if(is_clus):
            lists = clus.layout_clustering(img_path, elements, texts, self.clus_dir)
        else:
            lists, _ = load_lists_json(pjoin(self.clus_dir, name + '.json'))

        if(is_layout):
            layout, html_res = lay.recognize_layout(img_path, layout, elements, texts, lists, self.layout_dir)
        else:
            layout, html_res, _ = load_layout_json(self.layout_dir, name)

        return layout.generate_ele_list(), html_res