# -*- coding: utf-8 -*-
from qtpy import QtCore


class MidiSplit(QtCore.QObject):

    note = QtCore.Signal(object)
    # pitch  = QtCore.Signal(object)
    control = QtCore.Signal(object)
    program = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(MidiSplit, self).__init__(parent)

    @QtCore.Slot(object)
    def split(self, m):
        if m.isNoteOnOrOff():
            self.note.emit(m)
        # elif m.isPitchWheel() :
        #    self.pitch.emit(m)
        elif m.isController() or m.isPitchWheel():
            self.control.emit(m)
        elif m.isProgramChange():
            self.program.emit(m)
