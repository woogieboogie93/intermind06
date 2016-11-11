#_*_coding: utf-8

from transform import four_point_transform
import imutils
from skimage.filters import threshold_adaptive
import numpy as np
import cv2
from matplotlib import pyplot as plt


def preprocess(filename, userID, traineddata):
    if rotatePaper(filename, userID, traineddata) == -1 :
        if binarize(filename, userID, traineddata) == -1 :
            return -1
        
    #os.system('del %s' % filename)
    return 0

def binarize(filename, userID, traineddata):
    img = cv2.imread(filename, 0)

    if img == None:
        return -1
        
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #img = threshold_adaptive(img, 251, offset = 10)
    
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # Otsu's Thresholding after (앞에서 해줄수)
    ret3, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
    # morphological opening (글자가 뭉개짐)
    #kernel = np.ones((3, 3), np.uint8) # (x, y) 크기로 open하는듯
    #img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    preFilename = filename
    filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
        
    cv2.imwrite(filename, img)

    return 0
    
def rotatePaper(filename, userID, traineddata):
        image = cv2.imread(filename)
        if image == None:
            return -1
        ratio = image.shape[0] / 500.0
        orig = image.copy()
        image = imutils.resize(image, height = 500)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(image, (5, 5), 0)
        edged = cv2.Canny(gray, 75, 200)
 
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
 
        for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                        screenCnt = approx
                        break

        try:
            warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        except:
            return -1
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        warped = threshold_adaptive(warped, 251, offset = 10)
        warped = warped.astype("uint8") * 255

        filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
        cv2.imwrite(filename,warped)

        return 0
        

if __name__ == '__main__':
        print preprocess('image2.jpg','final',19)
