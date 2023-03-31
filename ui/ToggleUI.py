from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.syncObjectUI import Sync


class ToggleUI(QtWidgets.QCheckBox):
    def __init__(
        self,
        parent=None,
        value=False,
        repeat=True,
        syncModule="synced",
        syncName="",
        syncSave=True,
        serialize=True,
    ):
        QtWidgets.QCheckBox.__init__(self, parent)

        # synchronisation & serialization
        self._sync = Sync(self, syncModule=syncModule, syncName=syncName, save=syncSave)
        self.toggled.connect(self._sync.input)
        self._sync.output[bool].connect(self.setValue)
        self._serialize = serialize

        # self.setTristate(False)
        self._repeat = repeat
        self.setValue(value)

    # slot / property

    @QtCore.Slot(int)
    @QtCore.Slot(bool)
    def setValue(self, b):
        b = bool(b)
        if b == self.isChecked() and self._repeat:
            self.toggled.emit(b)
        else:
            self.setChecked(bool(b))

    value = QtCore.Property(bool, QtWidgets.QCheckBox.isChecked, setValue)

    # events

    def mousePressEvent(self, event):
        QtWidgets.QCheckBox.click(self)

    def mouseReleaseEvent(self, event):
        pass

    # synchro et serialisation
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

    # serialization

    def setSerialize(self, value):
        self._serialize = value

    def getSerialize(self):
        return self._serialize

    serialize = QtCore.Property(bool, getSerialize, setSerialize)

    def __getstate__(self):
        if self._serialize:
            return {"value": self.value}


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ToggleUI()
    widget.show()
    app.exec_()
