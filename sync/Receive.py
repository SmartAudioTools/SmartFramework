from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync import syncModules, SyncModule, SyncData


class Receive(QtCore.QObject):
    # signaux
    output = QtCore.Signal((object,), (bool,), (int,), (float,), (str,), (QtGui.QColor,))

    def __init__(self, parent=None, syncModule="synced", syncName=""):
        super(Receive, self).__init__(parent)
        self._syncModule = syncModule
        self._syncName = syncName
        self.updateSyncData()
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation

    def setSyncName(self, syncName):
        self._syncName = syncName
        self.updateSyncData()

    def getSyncName(self):
        return self._syncName

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncModule(self, value):
        self._syncModule = value
        self.updateSyncData()

    def getSyncModule(self):
        return self._syncModule

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def updateSyncData(self):
        syncName = self._syncName
        syncModule = self._syncModule
        if syncName:
            if not syncModule in syncModules:
                # print("attention creation d'un coll avant son interface")
                syncModules[syncModule] = SyncModule(syncModule=syncModule)
            if not syncName in syncModules[syncModule].__dict__:
                # print("creation du save Miror")
                syncModules[syncModule].__dict__[syncName] = SyncData(
                    syncModule, syncName
                )  # creer l'objet miroir qui va stocker la valeure et s'occuper d'envoyer a toutes les autres instance de save ayant le meme nom syncName
            self.syncData = syncModules[syncModule].__dict__[syncName]
            self.syncData.output.connect(self.receive)
            self.syncData._countReceive += 1

    def receive(self, obj):
        typeObj = type(obj)
        if typeObj in [bool, int, float, str, QtGui.QColor]:
            self.output[typeObj].emit(obj)
        if typeObj == int:
            self.output[float].emit(
                float(obj)
            )  # permet de recevoir un float meme si on a envoyé un int
        self.output[object].emit(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Receive()
    # widget.show()
    sys.exit(app.exec_())