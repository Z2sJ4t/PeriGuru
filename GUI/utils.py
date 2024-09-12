import cv2
from random import randint as rint

def ORB_siml(img1, img2):

    # Initialize ORB detector
    orb = cv2.ORB_create(nfeatures=200)

    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # Calculate the distance of special detection points using Hamming distance
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    # Using KNN algorithm for matching
    matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)

    # Remove blurry matching
    good = [(m, n) for (m, n) in matches if m.distance < 0.95 * n.distance and m.distance < 70]

    # Draw matching key points
    img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, img2, flags=2)
    cv2.imshow('img', img3)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    similary = len(good) / len(matches)
    return similary

def draw_label(img, loc, color=None, text=None, line=2, text_pos='l'):
    if(color is None):
        color = random_color()
    l, r, t, b = int(loc['left']), int(loc['right']), int(loc['top']), int(loc['bottom'])
    cv2.rectangle(img, (l, t), (r, b), color, line)
    if text is not None:
        # put text with rectangle
        (w,h),_ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        if(text_pos == 'l'):
            cv2.rectangle(img, (l, t - 20), (l + w, t - 20 + h), color, -1)
            cv2.putText(img, text, (l + 3, t - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        elif(text_pos == 'r'):
            cv2.rectangle(img, (r - w, t - 20), (r, t - 20 + h), color, -1)
            cv2.putText(img, text, (r - w + 3, t - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        elif(text_pos == 'm'):
            m = (l + r) / 2
            cv2.rectangle(img, (int(m - w/2), t - 20), (int(m + w/2), t - 20 + h), color, -1)
            cv2.putText(img, text, (int(m - w/2) + 3, t - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

def random_color():
    return rint(0, 255), rint(0, 255), rint(0, 255)