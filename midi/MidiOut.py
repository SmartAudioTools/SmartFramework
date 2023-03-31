# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework import midi


class MidiOut(QtCore.QObject):
    def __init__(self, parent=None, device=None):
        super(MidiOut, self).__init__(self, parent)
        self._device = None
        if device:
            self.setDevice(device)

    @QtCore.Slot(str)
    def setDevice(self, device):
        if self._device:
            midi.outDevices[self._device].stopDeviceIfLast()
        if device:
            if device in midi.outDevices:
                midi.outDevices[device].startDevice()
                self._device = device
                return
            else:
                print(f"le device MIDI {device} n'est pas branché")
        self._device = None

    def getDevice(self):
        return self._device

    device = QtCore.Property(str, getDevice, setDevice)

    @QtCore.Slot(object)
    def input(self, m):
        if self._device != None and self._device in midi.outDevices:
            # print(f'{self._device}: {m}')
            midi.outDevices[self._device].input(m)
            # print('.',)
        else:
            print("aucune sortie MIDI definie")
