from fourPointTransformUtility import four_point_tranform
from skimage.filters import threshold_local
import numpy as np
import cv2
import matplotlib.pyplot as plt
import imutils
import argparse
#construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required =True, help = "Path to input image to be scanned")
args = vars(ap.parse_args())


### EDGE DETECTION ###

#load the image and compute the ratio of the old height and the new height, clone it, and resize it
image = cv2.imread(args["image"])
ratio = image.shape[0]/ 500.0
orig = image.copy()
image = imutils.resize(image, height =500)

#convert the image to grayscale. blur it, and find edges

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5,5), 0)
edged = cv2.Canny(gray , 75, 200)

#show the original image and the edge detected image
cv2.imshow("Image", image)
cv2.imshow("Edged", edged)
#cv2.waitKey(0)


### FINDING CONTOURS ###

cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

# loop over the contours

for c in cnts:
	#approx the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02*peri, True)

	# if our ppriximated contour has 4 points, then we can assume that we have found our screen

	if(len(approx) ==4):
		screenCnt = approx
		break

#show the contour(outline) of the piece of paper
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("outline", image)
#cv2.waitKey()
#cv2.destroyAllWindows()


### APPLY A PERSPECTTIVE TRANSFORM AND THRESHOLD

#apply the four point transform to obtain a top-down view of the original image

warped = four_point_tranform(orig, screenCnt.reshape(4,2)*ratio)

#convert the warped image to grayscale, then threshold it to give that 'black and white' paper effect
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
T = threshold_local(warped, 11, offset = 10, method = "gaussian")
warped = (warped > T).astype("uint8")*255

#show the original and scanned images
cv2.imshow("original", imutils.resize(orig, height = 650))
cv2.imshow("Scanned", imutils.resize (warped, height = 650))
cv2.waitKey(0)

