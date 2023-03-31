# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework import midi

# from SmartFramework.sync.syncObjectUI import SyncObjectUI
from SmartFramework.sync.Sync import Sync


class MidiOutMenuUI(QtWidgets.QComboBox):
    outDevice = QtCore.Signal(str)

    def __init__(
        self,
        parent=None,
        syncModule="synced",
        syncName="",
        syncSave=True,
        serialize=True,
    ):
        QtWidgets.QComboBox.__init__(self, parent)

        # synchronisation & serialization
        self._sync = Sync(self, syncModule, syncName, syncSave)
        self._sync.output[str].connect(self.setDevice)
        self.currentTextChanged.connect(self._sync.input)
        self._serialize = serialize

        # SyncObjectUI.__init__(self,parent,syncName = 'MidiOut1')		# appel constructeur de la Classe de base
        # self.outDevice.connect(self._sync.input)	# connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable
        # self._sync.output.connect(self.setDevice)	# connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable

        # self.comBox = QtWidgets.QComboBox(self)
        self.addItems(midi.outDeviceNames)
        self.setCurrentIndex(-1)
        self.currentTextChanged.connect(self.outDevice)
        self.currentTextChanged.connect(self.recDesiredDevice)

    # properties
    @QtCore.Slot(str)
    def setDevice(self, name):
        self.recDesiredDevice(name)
        index = self.findText(name)
        if index != -1:
            self.setCurrentIndex(index)

    def recDesiredDevice(self, name):
        self.desiredDevice = name

    def getDevice(self):
        return self.currentText()

    device = QtCore.Property(str, getDevice, setDevice)

    # serialization

    def setSerialize(self, value):
        self._serialize = value

    def getSerialize(self):
        return self._serialize

    serialize = QtCore.Property(bool, getSerialize, setSerialize)

    def __getstate__(self):
        if hasattr(self, "desiredDevice"):
            return {"device": self.desiredDevice}

    # sync
    def setSyncModule(self, value):
        self._sync.syncModule = value

    def getSyncModule(self):
        return self._sync.syncModule

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        self._sync.syncName = value
        # print('setSyncName : ' + value)

    def getSyncName(self):
        return self._sync.syncName

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        self._sync.save = value

    def getSyncSave(self):
        return self._sync.save

    syncSave = QtCore.Property(bool, getSyncSave, setSyncSave)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MidiOutMenuUI()
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
