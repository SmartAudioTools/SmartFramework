# -*- coding: utf-8 -*-
from qtpy import QtCore
import numpy as np
import cv2


class ImageConvert(QtCore.QObject):
    # constructor
    def __init__(self, parent=None, inFormat="", outFormat=""):
        super(ImageConvert, self).__init__(parent)

    # signaux
    outImage = QtCore.Signal(
        [object], [QtCore.QPixmap], [QtCore.QImage], [QtCore.QPicture]
    )

    # slot
    @QtCore.Slot(object)
    def inImage(self, imageNumpy):
        pass

    def numpyToPixmap(imageNumpy):
        pass
