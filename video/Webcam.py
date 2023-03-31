# -*- coding: utf-8 -*-
from qtpy import QtCore, QtWidgets
from SmartFramework.video import webcams

# from SmartFramework.serialize import serializejson
# import os
# cameraIntrinsics_path = os.path.dirname(__file__)+"/cameraIntrinsics.json"
# cameraIntrinsics = serializejson.load(cameraIntrinsics_path)


class Webcam(QtCore.QObject):

    outImage = QtCore.Signal(object)
    outMode = QtCore.Signal(str)
    outResolution = QtCore.Signal(str)
    outFps = QtCore.Signal(int)
    outGain = QtCore.Signal(int)
    outExposure = QtCore.Signal(int)
    outWhiteBalance = QtCore.Signal(object)
    outWhiteBalanceR = QtCore.Signal(int)
    outWhiteBalanceG = QtCore.Signal(int)
    outWhiteBalanceB = QtCore.Signal(int)
    outLed = QtCore.Signal(bool)
    outEnableSettings = QtCore.Signal(bool)
    outDevice = QtCore.Signal(str)
    outDeviceID = QtCore.Signal(str)
    # outCameraIntrinsic = QtCore.Signal(object)

    def __init__(self, parent=None, device=None, autoStart=True):
        super(Webcam, self).__init__(parent)
        self.__dict__["device"] = None
        self._connectedDevice = None
        self._running = False

        # utilise syntaxe longue pour pouvoir stocker timer dans un attribut et eviter de lancer deux fois dans setAutoStart et dans setDevice
        self._singleShot = QtCore.QTimer(self)
        self._singleShot.setSingleShot(True)
        self._singleShot.timeout.connect(self.start)
        self.devicesSetting = {}

        self.setAutoStart(autoStart)
        if device:
            self.setDevice(device)

    # slots / Porperties / Methodes

    @QtCore.Slot()
    def start(self):
        # print("try start webcam")
        if self.device and not self._running:
            self._connectedDevice.startDevice()
            self._running = True

    @QtCore.Slot()
    def stop(self):
        if self.device and self._running:
            self._connectedDevice.stopDeviceIfLast()
            self._running = False

    @QtCore.Slot(bool)
    def startStop(self, b):
        if b:
            self.start()
        else:
            self.stop()

    @QtCore.Slot(str)
    def setDevice(self, device):
        if device in webcams.devices:
            # print('set Device !',)
            # print(device)

            if device == self.device:
                self.setDefaultSetting(device)
            else:
                wasRunning = self._running
                if self._connectedDevice:
                    self._connectedDevice.outImage.disconnect(self.outImage)
                    self.stop()
                self.__dict__[
                    "device"
                ] = device  # ne pas le deplacer car self.device doit être à jour pour self.start()
                self._connectedDevice = webcams.devices[self.device]
                if device not in self.devicesSetting:
                    if self._connectedDevice.enableSettings:
                        videoCapture = self._connectedDevice.videoCapture
                        # recupère les valeures par defaut pour les metre dans self.devicesSetting[device] et les afficher sur les controlUI
                        self.devicesSetting[device] = {
                            #'autoExposure' : ,
                            #'autoGain' : ,
                            #'autoWhiteBalance' : ,
                            #'autostart' : self.False,
                            "mode": videoCapture.mode,
                            #'device' : self.u'SmartCam',
                            "exposure": videoCapture.exposure,
                            "fps": videoCapture.fps,
                            "gain": videoCapture.gain,
                            "led": videoCapture.led,
                            #'paddingChannel' : True,
                            "resolution": videoCapture.resolution,
                            #'rotation' : self.setRotation,
                            "whiteBalance": videoCapture.whiteBalance,
                        }
                        # renvoit les valeurs qui on déjà ete emises si dans devicesSetting  mais permet d'avoir valeur par default si on n'en a jamais défini à la main
                        self.outMode.emit(videoCapture.mode)
                        self.outResolution.emit(videoCapture.resolution)
                        self.outFps.emit(videoCapture.fps)
                        self.outGain.emit(videoCapture.gain)
                        self.outExposure.emit(videoCapture.exposure)
                        self.outWhiteBalance.emit(videoCapture.whiteBalance)
                        self.outWhiteBalanceR.emit(videoCapture.whiteBalance[0])
                        self.outWhiteBalanceG.emit(videoCapture.whiteBalance[1])
                        self.outWhiteBalanceB.emit(videoCapture.whiteBalance[2])
                        self.outLed.emit(videoCapture.led)
                else:
                    self.setDefaultSetting(device)
                self.outEnableSettings.emit(self._connectedDevice.enableSettings)
                self.outDevice.emit(self.device)
                self.outDeviceID.emit(self._connectedDevice.deviceID)
                # self._emitCameraIntrinsic()
                self._connectedDevice.outImage.connect(self.outImage)
                if wasRunning:
                    self.start()
                elif self._autoStart:
                    # permet de demarer des qu'on a un nom de device si autoStart True
                    self._singleShot.start()

    def setDefaultSetting(self, device):
        if device in self.devicesSetting:
            keyToSetter = {
                "autoExposure": self.setAutoExposure,
                "autoGain": self.setAutoGain,
                "autoWhiteBalance": self.setAutoWhiteBalance,
                #'autostart' : self.False,
                "mode": self.setMode,
                #'device' : self.u'SmartCam',
                "exposure": self.setExposure,
                "fps": self.setFps,
                "gain": self.setGain,
                "led": self.setLed,
                #'paddingChannel' : True,
                "resolution": self.setResolution,
                "rotation": self.setRotation,
                "whiteBalance": self.setWhiteBalance,
            }
            for key, value in self.devicesSetting[device].items():
                if key in keyToSetter:
                    keyToSetter[key](value)

    def getDevice(self):
        return self.__dict__["device"]

    device = QtCore.Property(str, getDevice, setDevice)

    # properties
    def setAutoStart(self, autoStart):
        self._autoStart = autoStart
        if autoStart:
            self._singleShot.start()
        else:
            self._singleShot.stop()

    def getAutoStart(self):
        return self._autoStart

    autoStart = QtCore.Property(bool, getAutoStart, setAutoStart)

    # interface pour cleye

    @QtCore.Slot(int)
    def setRotation(self, value):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["rotation"] = value
            self._connectedDevice.setRotation(value)

    @QtCore.Slot(str)
    def setMode(self, mode):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["mode"] = mode
            self._connectedDevice.setMode(mode)
            self.outMode.emit(mode)

    @QtCore.Slot(str)
    def setResolution(self, resolution):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["resolution"] = resolution
            self._connectedDevice.setResolution(resolution)
            self.outResolution.emit(resolution)

    @QtCore.Slot(int)
    def setFps(self, fps):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["fps"] = fps
            self._connectedDevice.setFps(fps)
            self.outFps.emit(fps)

    @QtCore.Slot(bool)
    def setAutoGain(self, value):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["autoGain"] = value
            self._connectedDevice.setAutoGain(value)
            if value:
                self.outGain.emit("auto")

    @QtCore.Slot(int)
    def setGain(self, value):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["gain"] = value
            self._connectedDevice.setGain(value)
            self.outGain.emit(value)

    @QtCore.Slot(bool)
    def setAutoExposure(self, value):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["autoExposure"] = value
            self._connectedDevice.setAutoExposure(value)
            if value:
                self.outExposure.emit("auto")

    @QtCore.Slot(int)
    def setExposure(self, value):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["exposure"] = value
            self._connectedDevice.setExposure(value)
            self.outExposure.emit(value)

    @QtCore.Slot(bool)
    def setAutoWhiteBalance(self, value):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["autoWhiteBalance"] = value
            self._connectedDevice.setAutoWhiteBalance(value)
            if value:
                self.outWhiteBalance.emit("auto")

    # def setWhiteBalance(self, r, g, b):
    #    self._connectedDevice.setWhiteBalance(r, g, b)

    def setWhiteBalance(self, rgb):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["whiteBalance"] = rgb
            self._connectedDevice.setWhiteBalance(rgb)
            self.outWhiteBalance.emit(self._connectedDevice.videoCapture.whiteBalance)
            self.outWhiteBalanceR.emit(rgb[0])
            self.outWhiteBalanceG.emit(rgb[1])
            self.outWhiteBalanceB.emit(rgb[2])

    @QtCore.Slot(int)
    def setWhiteBalanceR(self, r):
        if self.device:
            self._connectedDevice.setWhiteBalanceR(r)
            self.outWhiteBalance.emit(self._connectedDevice.videoCapture.whiteBalance)
            self.outWhiteBalanceR.emit(r)

    @QtCore.Slot(int)
    def setWhiteBalanceG(self, g):
        if self.device:
            self._connectedDevice.setWhiteBalanceG(g)
            self.outWhiteBalance.emit(self._connectedDevice.videoCapture.whiteBalance)
            self.outWhiteBalanceG.emit(g)

    @QtCore.Slot(int)
    def setWhiteBalanceB(self, b):
        if self.device:
            self._connectedDevice.setWhiteBalanceB(b)
            self.outWhiteBalance.emit(self._connectedDevice.videoCapture.whiteBalance)
            self.outWhiteBalanceB.emit(b)

    @QtCore.Slot(bool)
    def setLed(self, value):
        if self.device and self._connectedDevice.enableSettings:
            self.devicesSetting[self.device]["led"] = value
            self._connectedDevice.setLed(value)
            self.outLed.emit(value)

    def __getstate__(self):
        state = dict()
        # if self._connectedDevice :
        state["device"] = self.device
        state["devicesSetting"] = self.devicesSetting
        # if self._connectedDevice.enableSettings :
        #    state.update(self._connectedDevice.videoCapture.__dict__)
        # else :
        return state

    def __setstate__(self, state):
        self.devicesSetting = state["devicesSetting"]
        if "device" in state:
            self.setDevice(state["device"])

    # def _emitCameraIntrinsic(self):
    #    deviceID = self._connectedDevice.deviceID
    #    cameraIntrinsic = cameraIntrinsics.get(deviceID,None)
    #    if cameraIntrinsic is None :
    #       print(f"Can't found calibration for {deviceID} in {cameraIntrinsics_path}")
    #    self.outCameraIntrinsic.emit(cameraIntrinsic)
