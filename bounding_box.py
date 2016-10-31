import numpy as np
import cv2

im = cv2.imread('opqr.png')
im2 = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
contours, hierarchy = cv2.findContours(im2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for i in range(0, len(contours)):
    if i % 2 == 0:
        cnt = contours[i]
        x, y, w, h = cv2.boundingRect(cnt)
        roi = im[y:y+h, x:x+w]
        #cv2.rectangle(im, (x, y), (x+w, y+h), (0,255,0),2)
        cv2.imshow('Features', im)
        cv2.imwrite(str(i) + '.png', roi)

cv2.destroyAllWindows()        
