from qtpy import QtWidgets
from SmartFramework.sync.SyncInterface import SyncInterface
from SmartFramework.files.FileSelectorUI import FileSelectorUI
from SmartFramework.sync.syncObjectUI import SyncObjectUI


class SyncPresetUI(SyncObjectUI):
    def __init__(
        self,
        parent=None,
        nombreFiles=4,
        dossierFiles="syncPresets",
        extension="dat",
        module="synced",
        saveLastWhenClose=True,
        format="tiny",
    ):
        SyncObjectUI.__init__(
            self, parent, syncModule="parameters", syncName="syncPresetSelected"
        )
        # self.__dict__.update(locals())     # suprimé pour éviter reférence circulaire lors de la sérialisation
        # pour qt designer et serialisation
        self.nombreFiles = nombreFiles
        self.dossierFiles = dossierFiles
        self.extension = extension
        self.saveLastWhenClose = saveLastWhenClose
        self.module = module
        self.format = format

        self.fileselectorui = FileSelectorUI(self, nombreFiles, dossierFiles, extension)
        self.syncinterface = SyncInterface(
            self, module, None, False, saveLastWhenClose, False, format, False, ""
        )

        self.fileselectorui.selectPath.connect(self.syncinterface.load)
        self.fileselectorui.oldPath.connect(self.syncinterface.save)
        self.fileselectorui.createAndSelectPath.connect(self.syncinterface.save)

        self._sync.output[str].connect(self.fileselectorui.setFile)
        self.fileselectorui.outputFileName.connect(self._sync.input)

    def __getstate__(self):
        if self.serialize:
            return {"fileselectorui": self.fileselectorui}
        else:
            pass

    def sizeHint(self):
        return self.fileselectorui.size()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = SyncPresetUI()
    widget.show()
    app.exec_()
