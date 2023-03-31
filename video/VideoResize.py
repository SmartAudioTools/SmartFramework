# -*- coding: utf-8 -*-
from qtpy import QtCore
import numpy as np
import cv2


class VideoResize(QtCore.QObject):

    # constructor
    def __init__(self, parent=None, ratio=1.0):
        super(VideoResize, self).__init__(parent)
        self._ratio = ratio

    # signaux
    outImage = QtCore.Signal(object)

    # slot
    @QtCore.Slot(object)
    def inImage(self, img):
        if self._ratio != 1.0:
            M = np.array([[self._ratio, 0, -0.5], [0, self._ratio, -0.5]])
            newsize = (int(self._ratio * img.shape[1]), int(self._ratio * img.shape[0]))
            imageResized = cv2.warpAffine(img, M, newsize)
            self.outImage.emit(imageResized)
        else:
            self.outImage.emit(img)

    # properties
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def setRatio(self, ratio):
        self._ratio = ratio

    def getRatio(self):
        return self._ratio

    ratio = QtCore.Property(float, getRatio, setRatio)
