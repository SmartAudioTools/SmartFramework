# -*- coding: utf-8 -*-
from qtpy import QtCore


class MidiPrint(QtCore.QObject):
    string = QtCore.Signal(str)

    def __init__(self, parent=None, consolePrint=True, prompt=""):
        super(MidiPrint, self).__init__(parent)
        self._connected = False
        self._prompt = prompt
        self.consolePrint = consolePrint  # sans '_' car fait appel à la propriété

    @QtCore.Slot(object)
    def printMessage(self, m):
        print(m)
        if m.isNoteOn():
            self.string.emit(
                "%sNoteOn  %s %d "
                % (self._prompt, m.getMidiNoteName(m.getNoteNumber()), m.getVelocity())
            )
        elif m.isNoteOff():
            self.string.emit(
                "%sNoteOff %s" % (self._prompt, m.getMidiNoteName(m.getNoteNumber()))
            )
        elif m.isController():
            self.string.emit(
                "%sControl %d %d"
                % (self._prompt, m.getControllerNumber(), m.getControllerValue())
            )
        elif m.isPitchWheel():
            self.string.emit("%sPitch   %d " % (self._prompt, m.getPitchWheelValue()))

    def consolePrintMethode(self, string):
        print(string)

    # proprietes
    def setConsolePrint(self, value):
        self._consolePrint = value
        if value:
            self._connected = True
            self.string.connect(self.consolePrintMethode)
        elif self._connected:
            self.string.disconnect(self.consolePrintMethode)

    def getConsolePrint(self):
        return self._consolePrint

    consolePrint = QtCore.Property(bool, getConsolePrint, setConsolePrint)

    def setPrompt(self, value):
        self._prompt = value

    def getPrompt(self):
        return self._prompt

    prompt = QtCore.Property(str, getPrompt, setPrompt)
