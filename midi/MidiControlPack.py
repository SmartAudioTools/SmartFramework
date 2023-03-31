# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework.tools.objects import add_Args
import rtmidi


class MidiControlPack(QtCore.QObject):
    control = QtCore.Signal(object)

    def __init__(self, parent=None, number=0, channel=1):
        super(MidiControlPack, self).__init__(parent)
        add_Args(locals())

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(int, int)
    @QtCore.Slot(float, int)
    @QtCore.Slot(int, int, int)
    @QtCore.Slot(float, int, int)
    def pack(self, value, number=None, channel=None):
        if number == None:
            number = self._number
        if channel == None:
            channel = self._channel
        if number == 128:  # pitch
            if type(value) == float:
                value = int(value * 16383.0 + 0.5)
            m = rtmidi.MidiMessage.pitchWheel(channel, value)
        else:
            if type(value) == float:
                value = int(value * 127.0 + 0.5)
            m = rtmidi.MidiMessage.controllerEvent(channel, number, value)
        self.control.emit(m)

    @QtCore.Slot(int)
    def setNumber(self, value):
        self._number = value

    def getNumber(self):
        return self._number

    number = QtCore.Property(int, getNumber, setNumber)

    @QtCore.Slot(int)
    def setChannel(self, value):
        self._channel = value

    def getChannel(self):
        return self._channel

    channel = QtCore.Property(int, getChannel, setChannel)
