from qtpy import QtCore, QtGui, QtWidgets
from .cleye import VideoCapture
from SmartFramework.string import toValidPath
from pybase64 import b64encode

DEBUG = False


class DeviceEye(QtCore.QThread):

    outImage = QtCore.Signal(object)
    outImageTimestamp = QtCore.Signal(object, object)

    def __init__(self, parent=None, deviceNum=0, fps=None):
        QtCore.QThread.__init__(self, parent)
        self.deviceNum = deviceNum
        self.fps = fps
        self.running = 0
        self.enableSettings = True

        if self.fps:
            self.videoCapture = VideoCapture(self.deviceNum, self.fps, autostart=False)
        else:
            self.videoCapture = VideoCapture(self.deviceNum, autostart=False)
        self.deviceID = "SmartCam[%s]" % toValidPath(
            b64encode(self.videoCapture._guid.__reduce__()[1][1][1]).decode("ascii")
        )

        if DEBUG:
            print("dans init :" + str(QtCore.QThread.currentThread()))

    def run(self):
        if DEBUG:
            print("start run")
        if DEBUG:
            print("dans run :" + str(QtCore.QThread.currentThread()))

        while self.running:
            frame = self.videoCapture.read()
            if frame is not None:
                self.outImage.emit(frame)

        if DEBUG:
            print("fini run")

    def startDevice(self):
        if not self.running:
            QtWidgets.QApplication.instance().lastWindowClosed.connect(self.__del__)
            self.running = 1
            self.videoCapture.start()
            self.start()
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
            self.exit()
            self.videoCapture.stop()
            # del(self.videoCapture) # prend du temps ! presque 1 seconde !!!! peut on le faire dans un autre thread ? va couper l'audio !

    def __del__(self):
        QtWidgets.QApplication.instance().lastWindowClosed.disconnect(self.__del__)
        self.stopDevice()

    def setRotation(self, value):
        self.videoCapture.setRotation(value)

    def setMode(self, mode):
        self.videoCapture.setMode(mode)

    def setResolution(self, resolution):
        self.videoCapture.setResolution(resolution)

    def setFps(self, fps):
        self.videoCapture.setFps(fps)

    def setAutoGain(self, value):
        self.videoCapture.setAutoGain(value)

    def setGain(self, value):
        self.videoCapture.setGain(value)

    def setAutoExposure(self, value):
        self.videoCapture.setAutoExposure(value)

    def setExposure(self, value):
        self.videoCapture.setExposure(value)

    def setAutoWhiteBalance(self, value):
        self.videoCapture.setAutoWhiteBalance(value)

    def setWhiteBalance(self, rgb):
        self.videoCapture.setWhiteBalance(rgb)

    def setWhiteBalanceR(self, r):
        self.videoCapture.setWhiteBalanceR(r)

    def setWhiteBalanceG(self, g):
        self.videoCapture.setWhiteBalanceG(g)

    def setWhiteBalanceB(self, b):
        self.videoCapture.setWhiteBalanceB(b)

    def setLed(self, value):
        self.videoCapture.setLed(value)
