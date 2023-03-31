from qtpy import QtCore, QtGui, QtWidgets
import rtmidi


# creation liste de noms de devices

inDeviceNames = []
outDeviceNames = []

midiin = rtmidi.RtMidiIn()  # Initialisation Entrée
deviceCount = midiin.getPortCount()  # nombre de devices disponibles
for i in range(deviceCount):
    inDeviceNames.append(midiin.getPortName(i))  # noms des ports

midiout = rtmidi.RtMidiOut()  # Initialisation Sortie
deviceCount = midiout.getPortCount()  # nombre de devices disponibles
for i in range(deviceCount):
    outDeviceNames.append(midiout.getPortName(i))

# print(inDeviceNames)
# print(outDeviceNames)
# creation dictionnaire de devices


class MidiInDevice(QtCore.QObject):
    output = QtCore.Signal(object)

    def __init__(self, parent=None, deviceNum=None):
        QtCore.QObject.__init__(self, parent)
        self.deviceNum = deviceNum
        self.running = 0

    def startDevice(self):
        if not self.running:
            self.rtMidiIn = rtmidi.RtMidiIn()  # Initialisation Entrée
            # enregistre la fonction de callback
            self.rtMidiIn.setCallback(self.callback)
            self.rtMidiIn.openPort(self.deviceNum)
            QtWidgets.QApplication.instance().lastWindowClosed.connect(self.stopDevice)
        self.running += 1

    def stopDeviceIfLast(self):
        if self.running == 1:
            self.stopDevice()
        else:
            self.running -= 1

    def stopDevice(self):
        QtWidgets.QApplication.instance().lastWindowClosed.disconnect(self.stopDevice)
        if self.running:
            self.running = 0
            self.rtMidiIn.closePort()
            # print("close port midi IN!")

    def callback(self, m):
        self.output[object].emit(m)


class MidiOutDevice(QtCore.QObject):
    def __init__(self, parent=None, deviceNum=None):
        QtCore.QObject.__init__(self, parent)
        self.deviceNum = deviceNum
        self.running = 0

    def startDevice(self):
        if not self.running:
            self.rtMidiOut = rtmidi.RtMidiOut()  # Initialisation Entrée
            self.rtMidiOut.openPort(self.deviceNum)
            QtWidgets.QApplication.instance().lastWindowClosed.connect(self.stopDevice)
        self.running += 1

    def stopDeviceIfLast(self):
        if self.running == 1:
            self.stopDevice()
        else:
            self.running -= 1

    def stopDevice(self):
        QtWidgets.QApplication.instance().lastWindowClosed.disconnect(self.stopDevice)
        if self.running:
            self.running = 0
            self.rtMidiOut.closePort()
            # print("close port midi OUT!")

    def input(self, obj):
        if self.running:
            self.rtMidiOut.sendMessage(obj)


inDevices = dict()
for deviceNum, deviceName in enumerate(inDeviceNames):
    inDevices[deviceName] = MidiInDevice(deviceNum=deviceNum)

outDevices = dict()
for deviceNum, deviceName in enumerate(outDeviceNames):
    outDevices[deviceName] = MidiOutDevice(deviceNum=deviceNum)
