import array
from time import perf_counter
from qtpy import QtCore, QtGui
from SmartFramework.events.threadSequencer import ThreadSequencer
from pygame import pypm
import numpy as np


# pypm.CountDevices()	  	# nombre d'entree + sorties MIDI
# GetDefaultInputDeviceID() 	# The default device can be specified using a small application named pmdefaults that is part of the PortMidi distribution.
# GetDefaultOutputDeviceID()


# (interf,name,input,output,opened) = pypm.GetDeviceInfo(num_device) 	# 	MMSystem,nom,1/0,1/0,1/0
# interf		underlying MIDI API, e.g. MMSystem or DirectX
# name 		device name, e.g. USB MidiSport 1x1
# input		true if input is available
# output		true if output is available
# opened 	used by generic PortMidi code to do error checking on arguments


def calibre():

    print("--- calibration decalage midi ---")

    duree_exp = 5.0
    debut_exp = perf_counter()
    fin_exp = duree_exp + debut_exp

    listeClock = []
    listePypmTime = []
    lastTime = pypm.Time()

    while perf_counter() < fin_exp:
        while lastTime == pypm.Time():
            pass
        lastTime = pypm.Time()
        listeClock.append(perf_counter())
        listePypmTime.append(lastTime)

    ArrayClock = np.array(listeClock)
    ArrayPypmTime = np.array(listePypmTime)
    moindreCarre = np.polyfit(ArrayPypmTime, ArrayClock, 1)
    offset = (
        moindreCarre[1] + 0.001
    )  # on se laisse 0.5 msec du au fluctuation du timer pypm et 0.5 msec du au fluctuation du timer Qt
    pente = moindreCarre[0]
    print("--- fin de calibration ------")
    return pente, offset


pypm.Initialize()
pente, offset = calibre()


class MidiDeviceIn(QtCore.QObject):

    output = QtCore.Signal(object)

    def __init__(self, parent=None, num_device=9, channelMask=None, datafilter=None):
        super(MidiDeviceIn, self).__init__(parent)

        self.midiIn = pypm.Input(num_device)
        QtWidgets.QApplication.instance().lastWindowClosed.connect(self.closeMidi)

        thread = self.thread()
        if not hasattr(thread, "threadSequencer"):
            thread.threadSequencer = ThreadSequencer(thread)
        thread.threadSequencer.getInputs.connect(self.read)

    def setChannelMask(self, mask):
        self.midiIn.SetChannelMask(pypm.Channel(1) | pypm.Channel(10))

    def setFilter(self, filter):
        self.midiIn.SetFilter(FILT_NOTE | FILT_CONTROL)

    def read(self):
        if self.midiIn.Poll():
            midiDatas = self.midiIn.Read(100)
            for midiData in midiDatas:
                date = midiData[1] * pente + offset
                # now = perf_counter()
                # if date < now :
                #    print("evenemnet enregistre dans passe de : " + str(date - now))
                data = midiData[0]
                event = (date, self.outData, data)
                self.thread().threadSequencer.recEvt(event)

    def closeMidi(self):
        QtWidgets.QApplication.instance().lastWindowClosed.disconnect(self.closeMidi)
        self.thread().threadSequencer.getInputs.disconnect(self.read)
        del self.midiIn

    def outData(self, data):
        # print(data)
        self.output[object].emit(data)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    widget.midiAllin = MidiDeviceIn()

    try:
        widget.show()
    except:
        pass

    sys.exit(app.exec_())
else:
    midiDeviceIn = MidiDeviceIn()
