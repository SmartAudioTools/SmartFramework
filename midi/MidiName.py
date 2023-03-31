from qtpy import QtCore
from rtmidi import MidiMessage


class MidiName(QtCore.QObject):

    noteNameSignal = QtCore.Signal(str, name="noteName")
    instrumentNameSignal = QtCore.Signal(str, name="instrumentName")
    bankNameSignal = QtCore.Signal(str, name="bankName")
    percusionNameSignal = QtCore.Signal(str, name="percusionName")
    controlNameSignal = QtCore.Signal(str, name="ControlName")

    def __init__(
        self,
        parent=None,
        useSharps=True,
        includeOctaveNumber=True,
        octaveNumForMiddleC=4,
    ):
        super(MidiName, self).__init__(pparent)
        self.useSharps = useSharps
        self.includeOctaveNumber = includeOctaveNumber
        self.octaveNumForMiddleC = octaveNumForMiddleC

    @QtCore.Slot(object)
    def name(self, m):
        if m.isNoteOnOrOff():
            self.instrumentName(m.getNoteNumber())
        elif m.isController():
            self.controlName(m.getControllerNumber())

    def noteName(self, m):
        self.noteNameSignal.emit(
            MidiMessage.getMidiNoteName(
                m, self._useSharps, self._includeOctaveNumber, self._octaveNumForMiddleC
            )
        )  # Returns the name of a midi note number. (E.g "C", "D#", etc.)

    @QtCore.Slot(int)
    def instrumentName(self, m):
        self.instrumentNameSignal.emit(
            MidiMessage.getGMInstrumentName(m)
        )  # Returns the standard name of a GM instrument. (instrument: 0 - 127)

    @QtCore.Slot(int)
    def bankName(self, m):
        self.bankNameSignal.emit(
            m.getGMInstrumentBankName(m)
        )  # Returns the name of a bank of GM instruments.(bank: 0 - 15)

    @QtCore.Slot(int)
    def percusionName(self, m):
        self.percusionNameSignal.emit(
            m.getRhythmInstrumentName(m)
        )  # Returns the standard name of a channel 10 percussion sound. (key: 35 - 81)

    @QtCore.Slot(int)
    def controlName(self, m):
        name = m.getControllerName(m)
        # Returns the name of a controller type number.
        self.controlNameSignal.emit(name)
