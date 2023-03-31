# -*- coding: utf-8 -*-
from qtpy import QtCore


class MidiNoteUnpack(QtCore.QObject):
    channel = QtCore.Signal(int)
    number = QtCore.Signal(int)
    velocity = QtCore.Signal((int,), (float,))

    def __init__(self, parent=None):
        super(MidiNoteUnpack, self).__init__(parent)

    @QtCore.Slot(object)
    def unpack(self, m):
        if m.isNoteOn():
            self.channel.emit(m.getChannel())
            self.velocity[int].emit(m.getVelocity())
            self.velocity[float].emit(m.getFloatVelocity())
            self.number.emit(m.getNoteNumber())

        elif m.isNoteOff():
            self.channel.emit(m.getChannel())
            self.velocity[int].emit(0)
            self.velocity[float].emit(0.0)
            self.number.emit(m.getNoteNumber())