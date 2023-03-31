# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework.tools.objects import add_Args
import rtmidi


class MidiNotePack(QtCore.QObject):
    note = QtCore.Signal(object)

    def __init__(self, parent=None, velocity=127, channel=1):
        super(MidiNotePack, self).__init__(parent)
        add_Args(locals())

    @QtCore.Slot(int)
    @QtCore.Slot(int, int)
    @QtCore.Slot(int, float)
    def pack(self, number, velocity=None, channel=None):
        if velocity == None:
            velocity = self._velocity
        if channel == None:
            channel = self._channel
        if velocity:
            if type(velocity) == float:
                velocity = int(velocity * 127.0 + 0.5)
            m = rtmidi.MidiMessage.noteOn(channel, number, velocity)
        else:
            m = rtmidi.MidiMessage.noteOff(channel, number)
        self.note.emit(m)

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def setVelocity(self, value):
        self._velocity = value

    def getVelocity(self):
        return self._velocity

    velocity = QtCore.Property(int, getVelocity, setVelocity)

    @QtCore.Slot(int)
    def setChannel(self, value):
        self._channel = value

    def getChannel(self):
        return self._channel

    channel = QtCore.Property(int, getChannel, setChannel)
