# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework.tools.objects import add_Args


class MidiChannelSelect(QtCore.QObject):

    select = QtCore.Signal(object)
    other = QtCore.Signal(object)

    def __init__(self, parent=None, omni=False, channel=0):
        super(MidiChannelSelect, self).__init__(parent)
        add_Args(locals())

    @QtCore.Slot(object)
    def filter(self, m):
        if self._omni or m.getChannel() == self._channel:
            self.select.emit(m)
        else:
            self.other.emit(m)

    @QtCore.Slot(bool)
    def setOmni(self, value):
        self._omni = value

    def getOmni(self):
        return self._omni

    omni = QtCore.Property(bool, getOmni, setOmni)

    @QtCore.Slot(int)
    def setChannel(self, value):
        self._channel = value

    def getChannel(self):
        return self._channel

    channel = QtCore.Property(int, getChannel, setChannel)
