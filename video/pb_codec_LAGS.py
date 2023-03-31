# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 12:23:15 2019

@author: Baptiste
"""
import cv2
import os

# from vidgear.gears import WriteGear

path = "D:/Baptiste.avi"
outPath = "D:/Baptiste2.avi"
codec = "LAGS"

# input
videoCapture = cv2.VideoCapture()
retval = videoCapture.open(path)
retval, image = videoCapture.read()
size = (image.shape[1], image.shape[0])

# output_params  = {"-vcodec":"libx264"}
# vidGearWriter = WriteGear(output_filename = "D:/Baptiste_vidGear.avi",**output_params) #Define writer


# output
fourcc = cv2.VideoWriter_fourcc(*str(codec))
videoWriter = cv2.VideoWriter()
videoWriteInColor = True
retval = videoWriter.open(outPath, cv2.CAP_VFW, fourcc, 30, size, videoWriteInColor)
print(retval)
while retval:
    videoWriter.write(image[:, :, 1])  # opencv
    # vidGearWriter.write(image[:,:,1])  # videoGear
    retval, image = videoCapture.read()
del videoWriter
os.system("pause")
