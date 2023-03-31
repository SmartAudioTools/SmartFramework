from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.video.webcams import deviceNames
from SmartFramework.sync.syncObjectUI import SyncObjectUI
from SmartFramework.sync import syncModules
from SmartFramework.sync.Sync import Sync


class SyncMenuUI(SyncObjectUI):
    output = QtCore.Signal((object,), (bool,), (int,), (float,), (str,), (QtGui.QColor,))

    def __init__(
        self,
        parent=None,
        selectedSyncName="",
        selectedSyncModule="synced",
        selectedSyncSave=True,
    ):
        SyncObjectUI.__init__(self, parent)  # appel constructeur de la Classe de base
        # connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable:
        self._sync.output[str].connect(self.setSelectedSyncName)
        self._selectedSyncSave = selectedSyncSave
        self._selectedSyncModule = selectedSyncModule
        self._selectedSyncName = selectedSyncName
        self.selectedSync = None
        QtCore.QTimer.singleShot(0, self.createItems)

        self.comBox = QtWidgets.QComboBox(self)
        self.comBox.setCurrentIndex(-1)
        self.comBox.currentTextChanged.connect(self.createSync)
        self.comBox.currentTextChanged.connect(self._sync.input)

    def createSync(self, selectedSyncName):
        if self.selectedSync:
            self.selectedSync.output.disconnect(self.output)
        self.selectedSync = Sync(
            self,
            syncModule=self._selectedSyncModule,
            syncName=selectedSyncName,
            save=self._selectedSyncSave,
        )
        self.selectedSync.output.connect(self.output)
        for t in [bool, int, float, str, QtGui.QColor]:
            self.selectedSync.output[t].connect(self.output[t])

    @QtCore.Slot(object)
    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    @QtCore.Slot(QtGui.QColor)
    def input(self, obj=None):
        if self.selectedSyncName:
            self.selectedSync.input(obj)

    def createItems(self):
        if self._selectedSyncModule in syncModules:
            keys = []
            for key in syncModules[self._selectedSyncModule].__dict__.keys():
                if key[0] != "_":
                    keys.append(key)
            self.comBox.addItems(keys)
            self.setSelectedSyncName(self._selectedSyncName)

    def __getstate__(self):
        if self.serialize:
            return {"webcam": self.webcam}

    # properties

    @QtCore.Slot(str)
    def setSelectedSyncName(self, name):
        index = self.comBox.findText(name)
        if index != -1:
            self.comBox.setCurrentIndex(index)
        else:
            self._selectedSyncName = name
            QtCore.QTimer.singleShot(0, self.setSelectedSyncNameDelayed)

    def setSelectedSyncNameDelayed(self):
        index = self.comBox.findText(self._selectedSyncName)
        if index != -1:
            self.comBox.setCurrentIndex(index)

    def getSelectedSyncName(self):
        return self.comBox.currentText()

    selectedSyncName = QtCore.Property(str, getSelectedSyncName, setSelectedSyncName)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = SyncMenuUI()
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()