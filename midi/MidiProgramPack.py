# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework.tools.objects import add_Args
import rtmidi


class MidiProgramPack(QtCore.QObject):
    program = QtCore.Signal(object)

    def __init__(self, parent=None, channel=1):
        super(MidiProgramPack, self).__init__(parent)
        add_Args(locals())

    @QtCore.Slot(int)
    def pack(self, number, channel=None):
        if channel == None:
            channel = self._channel
        m = rtmidi.MidiMessage.programChange(channel, number)
        self.program.emit(m)

    @QtCore.Slot(int)
    def setChannel(self, value):
        self._channel = value

    def getChannel(self):
        return self._channel

    channel = QtCore.Property(int, getChannel, setChannel)
