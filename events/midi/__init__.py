import array
from time import perf_counter
from qtpy import QtCore, QtGui
from SmartFramework.events.threadSequencer import ThreadSequencer
from pygame import pypm
import numpy as np


# pypm.CountDevices()	  	# nombre d'entree + sorties MIDI
# GetDefaultInputDeviceID() 	# The default device can be specified using a small application named pmdefaults that is part of the PortMidi distribution.
# GetDefaultOutputDeviceID()


# (interf,name,input,output,opened) = pypm.GetDeviceInfo(numDevice) 	# 	MMSystem,nom,1/0,1/0,1/0
# interf		underlying MIDI API, e.g. MMSystem or DirectX
# name 		device name, e.g. USB MidiSport 1x1
# input		true if input is available
# output		true if output is available
# opened 	used by generic PortMidi code to do error checking on arguments


def calibration():

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
pente, offset = calibration()
midiDeviceInDict = dict()
midiDeviceOutDict = dict()


class MidiDeviceIn(QtCore.QObject):

    output = QtCore.Signal(object)

    def __init__(self, parent=None, numDevice=9, channelMask=None, datafilter=None):
        super(MidiDeviceIn, self).__init__(parent)

        self.midiIn = pypm.Input(numDevice)
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
                print("read : " + str([data, date]))
                self.thread().threadSequencer.recEvt(event)

    def closeMidi(self):
        self.thread().threadSequencer.getInputs.disconnect(self.read)
        del self.midiIn

    def outData(self, data):
        # print(data)
        self.output[object].emit(data)


class MidiDeviceOut(QtCore.QObject):
    def __init__(self, parent=None, numDevice=9, latenceDevice=1):
        super(MidiDeviceOut, self).__init__(parent)

        self.midiOut = pypm.Output(numDevice, latenceDevice)  # Latence en millisecondes
        # si la latence est de <= 0 , le timestamps (date de sortie) est ignoré et les outputs sortent immédiatement
        # si la lentece est > 0 , le message sortira quand time_proc() >  timestamps (date de sortie)+ latence (calculé pour coller à la latence des buffeurs audios)
        QtWidgets.QApplication.instance().lastWindowClosed.connect(self.closeMidi)

    def closeMidi(self):
        del self.midiOut
