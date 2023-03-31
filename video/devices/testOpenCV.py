# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 17:21:17 2019

@author: Baptiste
"""
from time import sleep
import cv2

# cv2.destroyAllWindows()
videoCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
flag, frame = videoCapture.read()
print(flag, frame)
cv2.namedWindow("camera", 1)
while True:
    flag, frame = videoCapture.read()
    print(flag)
    if frame is not None:
        cv2.imshow("camera", frame)
    ch = cv2.waitKey(1)
    if ch == 27:
        break
del videoCapture
cv2.destroyWindow("camera")
