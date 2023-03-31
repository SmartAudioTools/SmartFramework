# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.Sync import Sync


styles = [
    "Windows",
    "WindowsXP",
    "WindowsVista",
    "Motif",
    "CDE",
    "Plastique",
    "Cleanlooks",
]


class StyleMenuUI(QtWidgets.QComboBox):
    def __init__(
        self,
        parent=None,
        syncModule="synced",
        syncName="",
        syncSave=True,
        serialize=True,
        style="",
    ):
        # les initArgs sont utiles pour avoir des valeure par defaut
        QtWidgets.QComboBox.__init__(self, parent)

        # synchronisation & serialization
        self._sync = Sync(self, syncModule, syncName, syncSave)
        self._sync.output[str].connect(self.setStyle)
        self.currentTextChanged.connect(self._sync.input)
        self._serialize = serialize

        self.addItems(styles)
        self.setCurrentIndex(-1)

        self.currentTextChanged.connect(self.applyStyle)
        self.setStyle(style)

    # properties

    @QtCore.Slot(str)
    def setStyle(self, style):
        if style is None:
            self.setCurrentIndex(-1)
        else:
            index = self.findText(style)
            if index != -1:
                self.setCurrentIndex(index)

    def getStyle(self):
        return self.currentText()

    style = QtCore.Property(str, getStyle, setStyle)

    def applyStyle(self, style):
        QtWidgets.QApplication.instance().setStyle(style)

    #  synchronisation

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
            return {"style": self.currentText()}


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MenuUI()
    widget.addItems(["oui", "non"])
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
