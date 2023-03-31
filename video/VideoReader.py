# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QFileDialog
import cv2


class VideoReader(QtCore.QObject):
    def __init__(self, parent=None, path=None):
        super(VideoReader, self).__init__(parent)
        self._running = False

        # videoReader
        self._videoCapture = cv2.VideoCapture()
        self.setPath(path)
        self._lastReadNb = -1

    # Signaux ------

    outImage = QtCore.Signal(object)
    outFrameCount = QtCore.Signal(int)
    outFrameNumber = QtCore.Signal(int)
    outFps = QtCore.Signal(float)

    # slots / Porperties / Methodes

    @QtCore.Slot(int)
    def readFrame(self, i, emit=True):
        if self._path is not None:
            # print(i)
            if i != self._lastReadNb + 1:
                self._videoCapture.set(cv2.CAP_PROP_POS_FRAMES, i)
            retval, image = self._videoCapture.read()
            if retval:
                image = image[:, :, 0]  # recupère que le premier layer ..... a revoir .
                self._lastReadNb = i
            if emit:
                self.outImage.emit(image)
            else:
                return image

    @QtCore.Slot()
    def open(self):
        path, filter = QFileDialog.getOpenFileName(
            self.parent(), "Open Video", "", "Video Files (*.avi)"
        )  # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner
        self.setPath(path)

    @QtCore.Slot(str)
    def setPath(self, path):
        self._path = path
        if path:
            retval = self._videoCapture.open(path)
            self.outFps.emit(self._videoCapture.get(cv2.CAP_PROP_FPS))
            self.outFrameCount.emit(
                int(self._videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
            )

    def getPath(self):
        return self._path

    path = QtCore.Property(str, getPath, setPath)


if __name__ == "__main__":
    import sys
    import os

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoReader()
    app.exec_()
