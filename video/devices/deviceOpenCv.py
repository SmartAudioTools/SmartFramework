from qtpy import QtCore, QtGui, QtWidgets
from cv2 import VideoCapture, CAP_DSHOW, __version__


class Device(QtCore.QObject):

    outImage = QtCore.Signal(object)

    def __init__(self, parent=None, deviceNum=None, fps=30.0, deviceID=None):
        super(Device, self).__init__(parent)
        self.deviceNum = deviceNum
        self.fps = fps
        self.running = 0
        self.timer = QtCore.QTimer()
        self.enableSettings = False
        self.deviceID = deviceID

    def startDevice(self):
        if not self.running:
            if __version__ < "4":
                self.videoCapture = VideoCapture(self.deviceNum)
            else:
                self.videoCapture = VideoCapture(self.deviceNum, CAP_DSHOW)
            QtWidgets.QApplication.instance().lastWindowClosed.connect(self.__del__)
            self.running = 1
            self.getFrame()
        else:
            self.running += 1

    def stopDeviceIfLast(self):
        if self.running == 1:
            self.stopDevice()
        else:
            self.running -= 1

    def stopDevice(self):
        if self.running:
            self.running = 0
            self.timer.stop()
            del (
                self.videoCapture
            )  # prend du temps ! presque 1 seconde !!!! peut on le faire dans un autre thread ? va couper l'audio !

    def __del__(self):
        QtWidgets.QApplication.instance().lastWindowClosed.disconnect(self.__del__)
        self.stopDevice()

    def getFrame(self):
        if self.running == 1:
            flag, frame = self.videoCapture.read()
            waitTime = 0  # va bloquer completement entre 2 images
            # (1000./self.fps) - 1     # on attend un peu moins pour eviter de louper des frames, sans pour autant bloquer trop la boucle d'evenemts.
            self.timer.singleShot(waitTime, self.getFrame)
            if frame is not None:
                self.outImage.emit(frame)

    def setRotation(self, value):
        pass  # self.videoCapture.setRotation(value)

    def setMode(self, mode):
        pass  # self.videoCapture.setMode(mode)

    def setResolution(self, resolution):
        pass  # self.videoCapture.setResolution(resolution)

    def setFps(self, fps):
        pass  # self.videoCapture.setFps(fps)

    def setAutoGain(self, value):
        pass  # self.videoCapture.setAutoGain(value)

    def setGain(self, value):
        pass  # self.videoCapture.setGain(value)

    def setAutoExposure(self, value):
        pass  # self.videoCapture.setAutoExposure(value)

    def setExposure(self, value):
        pass  # self.videoCapture.setExposure(value)

    def setAutoWhiteBalance(self, value):
        pass  # self.videoCapture.setAutoWhiteBalance(value)

    def setWhiteBalance(self, r, g, b):
        pass  # self.videoCapture.setWhiteBalance(r, g, b)

    def setWhiteBalanceR(self, r):
        pass  # self.videoCapture.setWhiteBalanceR(r)

    def setWhiteBalanceG(self, g):
        pass  # self.videoCapture.setWhiteBalanceG(g)

    def setWhiteBalanceB(self, b):
        pass  # self.videoCapture.setWhiteBalanceB(b)

    def setLed(self, value):
        pass  # self.videoCapture.setLed(value)
