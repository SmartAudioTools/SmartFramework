from qtpy import QtCore, QtWidgets
from SmartFramework.sync import syncModules, SyncModule


class SyncInterface(QtCore.QObject):
    def __init__(
        self,
        parent=None,
        module="synced",
        defaultFileName="",
        saveDefaultWhenClose=True,
        saveLastWhenClose=True,
        loadDefaultWhenOpen=True,
        format="tiny",
        setAttributes=False,
        filtre="",
    ):
        super(SyncInterface, self).__init__( parent)
        self.__dict__["module"] = module
        if module not in syncModules:
            # print("creation d'un syncModSerialize avec son interface")
            syncModules[module] = SyncModule(None, module)
        # syncModSerialize existait peut etre deja avant son interface'
        self.syncMod = syncModules[module]

        self.syncModSerialize = self.syncMod._serialize
        if defaultFileName:
            self.syncModSerialize.fileName = defaultFileName
        self.syncModSerialize.saveDefaultWhenClose = saveDefaultWhenClose
        self.syncModSerialize.saveLastWhenClose = saveLastWhenClose
        self.syncModSerialize.loadDefaultWhenOpen = loadDefaultWhenOpen
        self.syncModSerialize.format = format
        self.syncModSerialize.setAttributes = setAttributes
        self.syncModSerialize.filtre = filtre

    # slots

    @QtCore.Slot(str)
    def setFileName(self, fileName):
        self.__dict__["fileName"] = fileName
        self.syncModSerialize.setFileName(fileName)

    @QtCore.Slot()
    @QtCore.Slot(str)
    def saveLastAndLoad(self, fileName=None):
        self.syncModSerialize.saveLastAndLoad(fileName)

    @QtCore.Slot()
    @QtCore.Slot(str)
    def save(self, fileName=None):
        self.syncModSerialize.save(fileName)

    @QtCore.Slot()
    @QtCore.Slot(str)
    def load(self, fileName=None):
        self.syncModSerialize.load(fileName)

    @QtCore.Slot()
    def sendState(self):
        self.syncMod._sendState()

    def setModule(self, value):
        self.__dict__["module"] = value

    def getModule(self):
        return self.__dict__["module"]

    module = QtCore.Property(str, getModule, setModule)

    def setDefaultFileName(self, value):
        self.syncModSerialize.fileName = value

    def getDefaultFileName(self):
        return self.syncModSerialize.fileName

    defaultFileName = QtCore.Property(str, getDefaultFileName, setDefaultFileName)

    def setSaveDefaultWhenClose(self, value):
        self.syncModSerialize.saveDefaultWhenClose = value

    def getSaveDefaultWhenClose(self):
        return self.syncModSerialize.saveDefaultWhenClose

    saveDefaultWhenClose = QtCore.Property(
        bool, getSaveDefaultWhenClose, setSaveDefaultWhenClose
    )

    def setSaveLastWhenClose(self, value):
        self.syncModSerialize.saveLastWhenClose = value

    def getSaveLastWhenClose(self):
        return self.syncModSerialize.saveLastWhenClose

    saveLastWhenClose = QtCore.Property(
        bool, getSaveLastWhenClose, setSaveLastWhenClose
    )

    def setLoadDefaultWhenOpen(self, value):
        self.syncModSerialize.loadDefaultWhenOpen = value

    def getLoadDefaultWhenOpen(self):
        return self.syncModSerialize.loadDefaultWhenOpen

    loadDefaultWhenOpen = QtCore.Property(
        bool, getLoadDefaultWhenOpen, setLoadDefaultWhenOpen
    )

    def setFormat(self, value):
        self.syncModSerialize.format = value

    def getFormat(self):
        return self.syncModSerialize.format

    format = QtCore.Property(str, getFormat, setFormat)

    def setSetAttributes(self, value):
        self.syncModSerialize.setAttributes = value

    def getSetAttributes(self):
        return self.syncModSerialize.setAttributes

    setAttributes = QtCore.Property(bool, getSetAttributes, setSetAttributes)

    def setFiltre(self, value):
        self.syncModSerialize.filtre = value

    def getFiltre(self):
        return self.syncModSerialize.filtre

    filtre = QtCore.Property(str, getFiltre, setFiltre)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = SyncInterface()
    # widget.show()
    sys.exit(app.exec_())
