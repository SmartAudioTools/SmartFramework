# -*- coding: utf-8 -*-
from qtpy import QtCore
from SmartFramework.tools.objects import add_Args


class MidiFilter(QtCore.QObject):

    filtered = QtCore.Signal(object)
    other = QtCore.Signal(object)

    def __init__(self, parent=None, note=True, control=True, pitch=True, program=True):
        super(MidiFilter, self).__init__( parent)
        add_Args(locals())

    @QtCore.Slot(object)
    def filter(self, m):
        if m.isNoteOnOrOff() and self._note:
            self.filtered.emit(m)
        elif m.isPitchWheel() and self._pitch:
            self.filtered.emit(m)
        elif m.isController() and self._control:
            self.filtered.emit(m)
        elif m.isProgramChange() and self._program:
            self.filtered.emit(m)
        else:
            self.other.emit(m)
