# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework import midi


class MidiIn(QtCore.QObject):

    output = QtCore.Signal(object)

    def __init__(self, parent=None, device=None):
        super(MidiIn, self).__init__(parent)
        self._device = None
        if device:
            self.setDevice(device)

    @QtCore.Slot(str)
    def setDevice(self, device):
        if self._device:
            midi.inDevices[self._device].output.disconnect(self.output)
            midi.inDevices[self._device].stopDeviceIfLast()
        if device:
            midi.inDevices[device].output.connect(self.output)
            midi.inDevices[device].startDevice()
        self._device = device

    def getDevice(self):
        return self._device

    device = QtCore.Property(str, getDevice, setDevice)
