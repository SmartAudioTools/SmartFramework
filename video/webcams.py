# -*- coding: utf-8 -*-
import device
from SmartFramework.video.devices.deviceOpenCv import Device
from SmartFramework import nb_bits
from SmartFramework.string import toValidPath
from pybase64 import b64encode

# import sys

# globals ---------
deviceNames = []
devices = dict()

# creation des devices visibles par directX -----------------------

alldDeviceNames = device.getDeviceList()
for i, deviceName in enumerate(alldDeviceNames):
    if deviceName != "PS3Eye Camera":
        deviceNames.append(deviceName)
        devices[deviceName] = Device(deviceNum=i, deviceID=deviceName)
# except :
#    print("unable to enumerate directX camera (bug Ipython)")

# creation des PS3 Eye Devices ------------------------------------------------

if nb_bits == 32:
    from .devices.deviceEye import DeviceEye
    from .devices.cleye import cameraCount

    import __main__

    if hasattr(__main__, "__file__"):  # pour eviter de planter QtDesigner
        eyeNb = cameraCount()
        for i in range(eyeNb):
            if i > 0:
                deviceName = "SmartCam " + str(i + 1)
            else:
                deviceName = "SmartCam"
            deviceNames.append(deviceName)
            devices[deviceName] = DeviceEye(deviceNum=i)
