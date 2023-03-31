# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QFileDialog
import cv2


class VideoPlayer(QtCore.QObject):
    def __init__(self, parent=None, path=None):
        super(VideoPlayer, self).__init__(parent)
        self._running = False

        # VideoIndiceGenerator
        self._speed = 1.0
        self._readHead = -1
        self._step = 1
        self._fps = 30.0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)

        # videoReader
        self._videoCapture = cv2.VideoCapture()
        self.setPath(path)
        self._lastReadNb = -1

        # connexions

        self.outFrameNumber.connect(self.readFrame)

    # Signaux ------

    # VideoIndiceGenerator
    outFrameNumber = QtCore.Signal(int)
    outFrameCountLessOne = QtCore.Signal(int)

    # videoReader
    outImage = QtCore.Signal(object)
    outFrameCount = QtCore.Signal(int)
    outFps = QtCore.Signal(float)
    # outFrameNumber    = QtCore.Signal(int)

    # slots / Porperties / Methodes

    @QtCore.Slot()
    def start(self):
        self._readHead = -1
        self.play()

    @QtCore.Slot()
    def stop(self):
        self._readHead = -1
        self.pause()

    @QtCore.Slot(bool)
    def startStop(self, b):
        if b:
            self.start()
        else:
            self.stop()

    @QtCore.Slot()
    def play(self):
        self._running = True
        self.timer.start()

    @QtCore.Slot()
    def pause(self):
        self._running = False
        self.timer.stop()

    @QtCore.Slot(bool)
    def playPause(self, b):
        if b:
            self.play()
        else:
            self.pause()

    @QtCore.Slot()
    def tick(self):
        newHead = self._readHead + self._step
        if newHead >= 0.0 and newHead <= self._frameCount - 1:
            # si on le met aprés la lecteur fout la merde si boucle sur un slider:
            self._readHead = newHead
            self.outFrameNumber.emit(newHead)

    @QtCore.Slot()
    def next(self):
        newHead = self._readHead + 1
        if newHead <= self._frameCount - 1:
            # si on le met aprés la lecteur fout la merde si boucle sur un slider:
            self._readHead = newHead
            self.outFrameNumber.emit(newHead)

    @QtCore.Slot()
    def prev(self):
        newHead = self._readHead - 1
        if newHead >= 0.0:
            # si on le met aprés la lecteur fout la merde si boucle sur un slider:
            self._readHead = newHead
            self.outFrameNumber.emit(newHead)

    @QtCore.Slot(int)
    def inFrameNumber(
        self, i
    ):  # slot utilisé par slider pour eviter boucle , car pour slider setValue retourne une valeure...
        if self._readHead != i:
            self._readHead = i
            self.outFrameNumber.emit(self._readHead)

    @QtCore.Slot(float)
    def setSpeed(self, speed):
        if speed != 0.0:
            interval = abs(1000.0 / (self._fps * speed))
            self.timer.setInterval(interval)
            if speed > 0.0:
                self._step = 1
            else:
                self._step = -1
            if self._speed == 0.0:
                # redemarer si on avant précedement une vitesse nulle:
                self.timer.start()
        else:
            self.timer.stop()  # on arrète le timer car vitesse nulle...
        self._speed = speed

    """
    @QtCore.Slot(int)        
    def setFrameCount(self,i):
        self._frameCount = i
        self.outFrameCountLessOne.emit(i-1)
    
    @QtCore.Slot(float)
    def setFps(self, fps):
        self._fps = fps
    """
    # slots / Porperties / Methodes

    @QtCore.Slot(int)
    def readFrame(self, i, emit=True):
        # print(i)
        if i != self._lastReadNb + 1:
            self._videoCapture.set(cv2.CAP_PROP_POS_FRAMES, i)
        retval, image = self._videoCapture.read()
        if retval:
            # image = image[:,:,0]   # recupère que le premier layer ..... a revoir .
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
            self._videoCapture.set(
                cv2.CAP_PROP_POS_FRAMES, 0
            )  # permet d'eviter plantage avec certaines videos sur le premier read() , plantage pas forcement visible avec Qt !!??  ex de video : Marc_Boure_d=50_x=10_y=0_Mouth.avi
            self._fps = self._videoCapture.get(cv2.CAP_PROP_FPS)
            self._frameCount = int(self._videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.outFps.emit(self._fps)
            self.outFrameCount.emit(self._frameCount)
            self.outFrameCountLessOne.emit(self._frameCount - 1)

    def getPath(self):
        return self._path

    path = QtCore.Property(str, getPath, setPath)


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoPlayer()
    app.exec_()
