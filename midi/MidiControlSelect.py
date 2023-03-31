# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework.tools.objects import add_Args


class MidiControlSelect(QtCore.QObject):

    select = QtCore.Signal(object)
    value = QtCore.Signal((int,), (float,))
    other = QtCore.Signal(object)

    def __init__(self, parent=None, control=0):
        super(MidiControlSelect, self).__init__(parent)
        add_Args(locals())

    @QtCore.Slot(object)
    def filter(self, m):
        if m.isController() and m.getControllerNumber() == self._control:
            value = m.getControllerValue()
            self.select.emit(m)
            self.value[float].emit(value / 127.0)
            self.value[int].emit(value)
        elif m.isPitchWheel() and 128 == self._control:
            value = m.getPitchWheelValue()
            self.select.emit(m)
            self.value[float].emit(value / 16383.0)
            self.value[int].emit(value)
        else:
            self.other.emit(m)

    @QtCore.Slot(int)
    def setControl(self, value):
        self._control = value

    def getControl(self):
        return self._control

    control = QtCore.Property(int, getControl, setControl)