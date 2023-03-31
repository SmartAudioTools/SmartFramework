# -*- coding: utf-8 -*-
from qtpy import QtCore, QtWidgets



class VideoIndiceGenerator(QtCore.QObject):
    def __init__(self, parent=None):
        super(VideoIndiceGenerator,self).__init__(parent)
        self._running = False

        # videoIndiceGenerator
        self._speed = 1.0
        self._readHead = -1
        self._step = 1
        self._fps = 30.0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)

    # Signaux ------

    outFrameNumber = QtCore.Signal(int)
    outFrameCountLessOne = QtCore.Signal(int)
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

    @QtCore.Slot(int)
    def setFrameCount(self, i):
        self._frameCount = i
        self.outFrameCountLessOne.emit(i - 1)

    @QtCore.Slot(float)
    def setFps(self, fps):
        self._fps = fps


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoIndiceGenerator()
    app.exec_()
