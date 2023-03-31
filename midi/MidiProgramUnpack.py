# -*- coding: utf-8 -*-
from qtpy import QtCore


class MidiProgramUnpack(QtCore.QObject):
    channel = QtCore.Signal(int)
    number = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(MidiProgramUnpack, self).__init__(parent)

    @QtCore.Slot(object)
    def unpack(self, m):
        if m.isProgramChange():
            self.channel.emit(m.getChannel())
            self.number.emit(m.getProgramChangeNumber())
