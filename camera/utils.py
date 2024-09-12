import numpy as np
import cv2

def white_patch(img, percentile=85):
    threshold = np.percentile(img, percentile, axis=(0, 1))  
    normalized_image = np.clip(img.astype(float) / threshold, 0, 1)  
    white_patch_image = (normalized_image * 255).astype(np.uint8) 
    return white_patch_image

# Specify the height or width to resize image
def resize(img, width=None, height=None, inter=cv2.INTER_AREA):
    if(width is None and height is None):
        return img
    new_size = None
    (h, w) = img.shape[:2]
    if(width is None):
        r = height / float(h)
        new_size = (int(w * r), height)
    elif(height is None):
        r = width / float(w)
        new_size = (width, int(h * r))
    else:
        new_size = (width, height)
    return cv2.resize(img, new_size, interpolation=inter)

def show_image(img, title="img"):
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def Laplace_sharp(img):
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    laplacian = (laplacian + 127).astype('uint8')
    sharped_img = cv2.addWeighted(img, 2, laplacian, -1, 0)
    return sharped_img

def USM_sharp(img):
    blured = cv2.GaussianBlur(img, (5, 5), 1)
    sharped_img = cv2.addWeighted(img, 2, blured, -1, 0)
    return sharped_img