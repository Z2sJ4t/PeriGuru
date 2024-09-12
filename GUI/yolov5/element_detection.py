import time
import cv2
from os.path import join as pjoin
import torch

from ultralytics.utils.plotting import Annotator, colors

from third_party.yolov5.models.common import DetectMultiBackend
from third_party.yolov5.utils.dataloaders import LoadImages
from third_party.yolov5.utils.general import non_max_suppression, Profile, scale_boxes, check_img_size
from third_party.yolov5.utils.torch_utils import select_device

from GUI.data_structure.Element import Element
from GUI.data_structure.Element import save_elements_json

def element_detection(img_path, output_dir, 
    conf_thres=0.25, iou_thres=0.45,
    max_det=1000,
    hide_conf=False, hide_labels=False):
    start = time.perf_counter()
    name = img_path.replace('\\', '/').split('/')[-1][:-4]

    # Load model
    device = select_device("cpu")
    model = DetectMultiBackend('./third_party/yolov5/weights/best.pt', device=device, dnn=False, 
        data='./third_party/yolov5/data/VINS.pt', fp16=False)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size((640, 640), s=stride)  # check image size

    # Dataloader
    bs = 1  # batch_size
    dataset = LoadImages(img_path, img_size=imgsz, stride=stride, auto=pt, vid_stride=1)
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    seen, windows, dt = 0, [], (Profile(device=device), Profile(device=device), Profile(device=device))
    for path, im, im0s, vid_cap, s in dataset:
        with dt[0]:
            im = torch.from_numpy(im).to(model.device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim
            if model.xml and im.shape[0] > 1:
                ims = torch.chunk(im, im.shape[0], 0)

        # Inference
        with dt[1]:
            if model.xml and im.shape[0] > 1:
                pred = None
                for image in ims:
                    if pred is None:
                        pred = model(image, augment=False, visualize=False).unsqueeze(0)
                    else:
                        pred = torch.cat((pred, model(image, augment=False, visualize=False).unsqueeze(0)), dim=0)
                pred = [pred, None]
            else:
                pred = model(im, augment=False, visualize=False)
        # NMS
        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, None, False, max_det=max_det)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            seen += 1
            p, im0, frame = path, im0s.copy(), getattr(dataset, "frame", 0)

            s += "%gx%g " % im.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            annotator = Annotator(im0, line_width=2, example=str(names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                elements = []

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)  # integer class
                    label = names[c] if hide_conf else f"{names[c]}"
                    confidence = float(conf)
                    confidence_str = f"{confidence:.2f}"

                    location = {'left': int(xyxy[0]), 'top': int(xyxy[1]),
                        'right': int(xyxy[2]), 'bottom': int(xyxy[3])}
                    ele = Element(names[c], confidence, location)
                    elements.append(ele)

                    label = None if hide_labels else (names[c] if hide_conf else f"{names[c]} {conf:.2f}")
                    annotator.box_label(xyxy, label, color=colors(c, True))

            # Save results (image with detections)
            im0 = annotator.result()
            cv2.imwrite(pjoin(output_dir, name + '.jpg'), im0)
            save_elements_json(pjoin(output_dir, name + '.json'), elements, im0.shape)

    print("[Element Detection Completed in %.3f s] Input: %s Output: %s" % (time.perf_counter() - start, img_path, pjoin(output_dir, name+'.json')))
    return elements