from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.video.webcams import deviceNames

# from SmartFramework.sync.Sync import Sync
from SmartFramework.ui.ControlUI import ControlUI


class WebcamMenuUI(ControlUI):
    def __init__(
        self, parent=None, syncModule="synced", syncName="webcam", syncSave=False
    ):
        ControlUI.__init__(
            self,
            parent,
            prefix="Camera :",
            syncModule=syncModule,
            syncName=syncName,
            syncSave=syncSave,
            repeat=False,
            sendInitValue=True,
        )
        self.setItems(deviceNames)
        self.setCurrentIndex(-1)

        # properties

    @QtCore.Slot(str)
    def setDevice(self, name):
        self.setItem(name)

    def getDevice(self):
        return self._items[self.value]

    device = QtCore.Property(str, getDevice, setDevice)

    # sert juste à eviter que Python -> QtDesigner ne les recrée. idealement faudrait que le compilateur evite de les recrer si les methode existe dans une des classe dont l'objet hérite
    def setSyncModule(self, value):
        self._sync.syncModule = value

    def getSyncModule(self):
        return self._sync.syncModule

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        self._sync.syncName = value

    def getSyncName(self):
        return self._sync.syncName

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        self._sync.save = value

    def getSyncSave(self):
        return self._sync.save

    syncSave = QtCore.Property(bool, getSyncSave, setSyncSave)

    # serialization

    # def setSerialize(self,value):
    #    self._serialize = value
    # def getSerialize(self):
    #    return self._serialize
    # serialize = QtCore.Property(bool, getSerialize, setSerialize)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = WebcamMenuUI()
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
