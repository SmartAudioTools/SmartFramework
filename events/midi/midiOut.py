# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 16:03:32 2011

@author: guilbut
"""
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.events.threadSequencer import ThreadSequencer
import SmartFramework.events.midi as midi


class MidiOut(QtCore.QObject):
    def __init__(self, parent=None, numDevice=12):
        super(MidiOut, self).__init__(parent)

        if numDevice not in midi.midiDeviceOutDict:
            midi.midiDeviceOutDict[numDevice] = midi.MidiDeviceOut(numDevice=numDevice)
        self.midiDeviceOut = midi.midiDeviceOutDict[numDevice].midiOut

        thread = self.thread()
        if not hasattr(thread, "threadSequencer"):
            thread.threadSequencer = ThreadSequencer(thread)
        self.threadSequencer = thread.threadSequencer

    @QtCore.Slot(object)
    def write(self, data):
        date = self.threadSequencer.getTime()
        self.midiDeviceOut.Write([[data, date]])
        # envoit un liste de message MIDI (max 1024) avec des dates de sortie (Rem : les Datas 1 et 2 sont facultatives) si la lentece definie par pypm.Input() est > 0 , le message sortira quand time_proc() >  timestamps (date de sortie)+ latence (calculé pour coller à la latence des buffeurs audios)
        print("write" + str([data, date]))

    @QtCore.Slot(object)
    def writeNow(self, data):
        self.midiDeviceOut.WriteShort(
            Data
        )  # Envoit la donnée 0xCodeHexa  immediatement ( avec une latence definie par pypm.Output())  . (Rem : les Datas 1 et 2 sont facultatives)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    widget.midiAllin = MidiOut(widget)

    try:
        widget.show()
    except:
        pass

    sys.exit(app.exec_())
