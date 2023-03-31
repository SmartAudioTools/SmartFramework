from qtpy import QtCore, QtGui, QtWidgets
import SmartFramework.events.midi as midi


class MidiIn(QtCore.QObject):

    output = QtCore.Signal(object)

    def __init__(self, parent=None, numDevice=9):
        super(MidiIn, self).__init__(parent)

        if numDevice not in midi.midiDeviceInDict:
            midi.midiDeviceInDict[numDevice] = midi.MidiDeviceIn(numDevice=numDevice)
        midi.midiDeviceInDict[numDevice].output.connect(self.outData)

    def outData(self, data):
        print(data)
        self.output[object].emit(data)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    widget.midiAllin = MidiIn(widget)

    try:
        widget.show()
    except:
        pass

    sys.exit(app.exec_())
