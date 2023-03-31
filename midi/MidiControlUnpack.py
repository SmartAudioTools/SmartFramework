# -*- coding: utf-8 -*-
from qtpy import QtCore


class MidiControlUnpack(QtCore.QObject):
    channel = QtCore.Signal(int)
    number = QtCore.Signal(int)
    value = QtCore.Signal((int,), (float,))

    def __init__(self, parent=None, pitch=True):
        super(MidiControlUnpack, self).__init__(parent)
        self._pitch = pitch

    @QtCore.Slot(object)
    def unpack(self, m):
        if m.isController():
            number = m.getControllerNumber()
            value = m.getControllerValue()
            self.channel.emit(m.getChannel())
            self.number.emit(number)
            self.value[float].emit(value / 127.0)
            self.value[int].emit(value)

        if self._pitch and m.isPitchWheel():
            value = m.getPitchWheelValue()
            self.channel.emit(m.getChannel())
            self.number.emit(128)
            self.value[float].emit(value / 16383.0)
            self.value[int].emit(value)