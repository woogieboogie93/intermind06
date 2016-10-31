#_*_coding: utf-8

# import the necessary packages
from transform import four_point_transform
import imutils
from skimage.filters import threshold_adaptive
import numpy as np
import argparse
import cv2
 
# construct the argument parser and parse the arguments
# 이미지 가져옴
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "Path to the image to be scanned")
args = vars(ap.parse_args())

# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it
# 이미지를 읽음
image = cv2.imread(args["image"])
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)
 
# convert the image to grayscale, blur it, and find edges
# in the image
# 이진화 + GaussianBlur(노이즈 감소 + 디테일도 감소)
'''
GaussianBlur = GaussianFilter => 노이즈를 감소
노이즈랑 디테일 감소
반투명한 곳으로 보는거 같은데 포커스의 밖에 있는애들이나 조명의 그늘진 부분을
grayscale(이진화)를 이용해 기하학적 취급이 가능.
Canny edge detection을 이용해 테두리를 출력. (현재 최소 임계값 75, 최대 임계값 200).

Gaussian blur를 이용해 노이즈를 감소시키고
Canny edge detection을 이용해 테두리를 출력.
'''
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)
 
# show the original image and the edge detected image
print "STEP 1: Edge Detection"
cv2.imshow("Image", image)
cv2.imshow("Edged", edged)
cv2.waitKey(0)
cv2.destroyAllWindows()

# find the contours in the edged image, keeping only the
# largest ones, and initialize the screen contour
# contour이란 같은 값을 가진 곳들을 연결한 선. 이로 꼭지점 좌표얻
(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
 
# loop over the contours
for c in cnts:
	# approximate the contour
	# 꼭지점으로 부터 이미지 테두리 추출
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
 
	# if our approximated contour has four points, then we
	# can assume that we have found our screen
	if len(approx) == 4:
		screenCnt = approx
		break
 
# show the contour (outline) of the piece of paper
print "STEP 2: Find contours of paper"
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("Outline", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# apply the four point transform to obtain a top-down
# view of the original image
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
 
# convert the warped image to grayscale, then threshold it
# to give it that 'black and white' paper effect
#  이진화
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
warped = threshold_adaptive(warped, 251, offset = 10)
warped = warped.astype("uint8") * 255
 
# show the original and scanned images
print "STEP 3: Apply perspective transform"
cv2.imshow("Original", imutils.resize(orig, height = 650))
cv2.imshow("Scanned", imutils.resize(warped, height = 650))
cv2.imwrite(args["image"],warped)################################################
cv2.waitKey(0)
