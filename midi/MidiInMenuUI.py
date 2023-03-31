# -*- coding: utf-8 -*-
from qtpy import QtCore, QtWidgets
from SmartFramework import midi
from SmartFramework.sync.syncObjectUI import SyncObjectUI


class MidiInMenuUI(SyncObjectUI):
    outDevice = QtCore.Signal(str)

    def __init__(self, parent=None):
        # appel constructeur de la Classe de base :
        SyncObjectUI.__init__(self, parent, syncName="MidiIn1")
        # connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable:
        self.outDevice.connect(self._sync.input)
        # connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable:
        self._sync.output[str].connect(self.setDevice)

        self.comBox = QtWidgets.QComboBox(self)
        self.comBox.addItems(midi.inDeviceNames)
        self.comBox.setCurrentIndex(-1)
        self.comBox.currentTextChanged.connect(self.outDevice)

    # properties
    @QtCore.Slot(str)
    def setDevice(self, name):
        index = self.comBox.findText(name)
        if index != -1:
            self.comBox.setCurrentIndex(index)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MidiInMenuUI()
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
