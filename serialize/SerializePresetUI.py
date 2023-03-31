from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.serialize.SerializeInterface import SerializeInterface
from SmartFramework.files.FileSelectorUI import FileSelectorUI
from SmartFramework.sync.syncObjectUI import SyncObjectUI


class SerializePresetUI(SyncObjectUI):
    def __init__(
        self,
        parent=None,
        nombreFiles=4,
        dossierFiles="serializePresets",
        extension="dat",
        target="self.parent().parent",
        defaultFileName="",
        saveDefaultWhenClose=True,
        saveLastWhenClose=True,
        loadDefaultWhenOpen=True,
        format="python",
        setAttributes=True,
        filtre="_",
        roundFloat=0,
        space=True,
        readableArrayMaxSize=0,
        syncModule="synced",
        syncName="",
        syncSave=False,
        # serialize=False,
    ):
        SyncObjectUI.__init__(
            self,
            parent,
            syncModule=syncModule,
            syncName=syncName,
            syncSave=syncSave,
            # serialize=serialize,
        )
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        # self.serialize = serialize
        self.nombreFiles = nombreFiles
        self.dossierFiles = dossierFiles
        self.extension = extension
        self.fileselectorui = FileSelectorUI(self, nombreFiles, dossierFiles, extension)
        self.serializeinterface = SerializeInterface(
            self,
            target=target,
            fileName=defaultFileName,
            saveDefaultWhenClose=saveDefaultWhenClose,
            saveLastWhenClose=saveLastWhenClose,
            loadDefaultWhenOpen=loadDefaultWhenOpen,
            format=format,
            setAttributes=setAttributes,
            filtre=filtre,
            roundFloat=roundFloat,
            space=space,
            readableArrayMaxSize=readableArrayMaxSize,
        )

        self.fileselectorui.selectPath.connect(self.serializeinterface.load)
        self.fileselectorui.oldPath.connect(self.serializeinterface.save)
        self.fileselectorui.createAndSelectPath.connect(self.serializeinterface.save)

        self._sync.output[str].connect(self.fileselectorui.setFile)
        self.fileselectorui.outputFileName.connect(self._sync.input)

    def __getstate__(self):
        # if self.serialize:
        return {"fileselectorui": self.fileselectorui}
        # else:
        #    pass

    def sizeHint(self):
        return self.fileselectorui.size()

    def setNombreFiles(self, value):
        self.__dict__["nombreFiles"] = value

    def getNombreFiles(self):
        return self.__dict__["nombreFiles"]

    nombreFiles = QtCore.Property(int, getNombreFiles, setNombreFiles)

    def setDossierFiles(self, value):
        self.__dict__["dossierFiles"] = value

    def getDossierFiles(self):
        return self.__dict__["dossierFiles"]

    dossierFiles = QtCore.Property(str, getDossierFiles, setDossierFiles)

    def setExtension(self, value):
        self.__dict__["extension"] = value

    def getExtension(self):
        return self.__dict__["extension"]

    extension = QtCore.Property(str, getExtension, setExtension)

    def setTarget(self, value):
        self.serializeinterface.target = value

    def getTarget(self):
        return self.serializeinterface.target

    target = QtCore.Property(str, getTarget, setTarget)

    def setDefaultFileName(self, value):
        self.serializeinterface.fileName = value

    def getDefaultFileName(self):
        return self.serializeinterface.fileName

    defaultFileName = QtCore.Property(str, getDefaultFileName, setDefaultFileName)

    def setSaveDefaultWhenClose(self, value):
        self.serializeinterface.saveDefaultWhenClose = value

    def getSaveDefaultWhenClose(self):
        return self.serializeinterface.saveDefaultWhenClose

    saveDefaultWhenClose = QtCore.Property(
        bool, getSaveDefaultWhenClose, setSaveDefaultWhenClose
    )

    def setSaveLastWhenClose(self, value):
        self.serializeinterface.saveLastWhenClose = value

    def getSaveLastWhenClose(self):
        return self.serializeinterface.saveLastWhenClose

    saveLastWhenClose = QtCore.Property(
        bool, getSaveLastWhenClose, setSaveLastWhenClose
    )

    def setLoadDefaultWhenOpen(self, value):
        self.serializeinterface.loadDefaultWhenOpen = value

    def getLoadDefaultWhenOpen(self):
        return self.serializeinterface.loadDefaultWhenOpen

    loadDefaultWhenOpen = QtCore.Property(
        bool, getLoadDefaultWhenOpen, setLoadDefaultWhenOpen
    )

    def setFormat(self, value):
        self.serializeinterface.format = value

    def getFormat(self):
        return self.serializeinterface.format

    format = QtCore.Property(str, getFormat, setFormat)

    def setSetAttributes(self, value):
        self.serializeinterface.setAttributes = value

    def getSetAttributes(self):
        return self.serializeinterface.setAttributes

    setAttributes = QtCore.Property(bool, getSetAttributes, setSetAttributes)

    def setFiltre(self, value):
        self.serializeinterface.filtre = value

    def getFiltre(self):
        return self.serializeinterface.filtre

    filtre = QtCore.Property(str, getFiltre, setFiltre)

    def setRoundFloat(self, value):
        self.serializeinterface.roundFloat = value

    def getRoundFloat(self):
        return self.serializeinterface.roundFloat

    roundFloat = QtCore.Property(int, getRoundFloat, setRoundFloat)

    def setSpace(self, value):
        self.serializeinterface.space = value

    def getSpace(self):
        return self.serializeinterface.space

    space = QtCore.Property(bool, getSpace, setSpace)

    def setReadableArrayMaxSize(self, value):
        self.serializeinterface.readableArrayMaxSize = value

    def getReadableArrayMaxSize(self):
        return self.serializeinterface.readableArrayMaxSize

    readableArrayMaxSize = QtCore.Property(
        int, getReadableArrayMaxSize, setReadableArrayMaxSize
    )

    def setSyncModule(self, value):
        SyncObjectUI.setSyncModule(self, value)

    def getSyncModule(self):
        return SyncObjectUI.getSyncModule(self)

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        SyncObjectUI.setSyncName(self, value)

    def getSyncName(self):
        return SyncObjectUI.getSyncName(self)

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        SyncObjectUI.setSyncSave(self, value)

    def getSyncSave(self):
        return SyncObjectUI.getSyncSave(self)

    syncSave = QtCore.Property(bool, getSyncSave, setSyncSave)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = SerializePresetUI()
    widget.show()
    app.exec_()
