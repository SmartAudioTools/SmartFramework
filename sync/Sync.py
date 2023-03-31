﻿# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync import syncModules, SyncModule, SyncData


class Sync(QtCore.QObject):
    # signaux
    output = QtCore.Signal((object,), (bool,), (int,), (float,), (str,), (QtGui.QColor,))

    def __init__(self, parent=None, syncModule="synced", syncName="", save=True):
        super(Sync, self).__init__(parent)
        self.__dict__["syncModule"] = syncModule
        self.__dict__["syncName"] = syncName
        self.save = save
        self._receiveGate = 1
        self._inputGate = 1
        self._syncData = None
        self.updateSyncData()

    # slots

    @QtCore.Slot(object)
    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    @QtCore.Slot(QtGui.QColor)
    def input(self, obj=None):
        if self.syncName and self._inputGate:
            self._receiveGate = 0
            self._syncData.input(obj, self.save)
            self._receiveGate = 1  # ne marche pas en connexions queued ?

    def receive(self, obj):
        if self._receiveGate:
            self._inputGate = 0
            typeObj = type(obj)
            if typeObj in [bool, int, float, str, QtGui.QColor]:
                self.output[typeObj].emit(obj)
            if typeObj == int:
                self.output[float].emit(
                    float(obj)
                )  # permet de recevoir un float meme si on a envoyé un int
            self.output[object].emit(obj)
            self._inputGate = 1
        # else :                                 # permet de resoudre le problème de connexion queued ?
        #    self._receiveGate = 1

    def updateSyncData(self):
        syncName = self.syncName
        syncModule = self.syncModule

        if self._syncData:  # clean
            if (
                self._syncData.syncModule == syncModule
                and self._syncData.syncName == syncName
            ):
                # pas indispensable mais evite de redefinir self._syncData si rien n'a changé:
                return
            # print('deconnect _syncData : ' +  syncModule  + syncName)
            self._syncData.output.disconnect(self.receive)
            self._syncData._countReceive -= 1
            self._syncData._countSend -= 1
            oldsyncModuleStr = self._syncData.syncModule
            oldSyncModule = syncModules[oldsyncModuleStr]
            if self._syncData._countSend == 0 and self._syncData._countReceive == 0:
                oldSyncModule._sendStateSignal.disconnect(self._syncData.sendState)
                del oldSyncModule.__dict__[self._syncData.syncName]
                if list(oldSyncModule.__dict__.keys()) == [
                    "_serialize"
                ]:  #  oldsyncModule vide annule le singleshot
                    # print(oldsyncModuleStr + "vide annule le singleshot")
                    oldSyncModule._serialize._singleShot.stop()
                    del syncModules[oldsyncModuleStr]
            self._syncData = None

        if syncName and syncModule:
            if not syncModule in syncModules:
                # print("attention creation d'un coll avant son interface")
                syncModules[syncModule] = SyncModule(syncModule=syncModule)
            if not syncName in syncModules[syncModule].__dict__:
                # print("creation du save Miror")
                syncModules[syncModule].__dict__[syncName] = SyncData(
                    syncModule, syncName
                )  # creer l'objet miroir qui va stocker la valeure et s'occuper d'envoyer a toutes les autres instance de save ayant le meme nom syncName
            self._syncData = syncModules[syncModule].__dict__[syncName]
            self._syncData.output.connect(self.receive)
            self._syncData._countReceive += 1
            self._syncData._countSend += 1
            # print('connect   _syncData : ' +  syncModule  + syncName)

    def setSyncModule(self, value):
        self.__dict__["syncModule"] = value
        self.updateSyncData()

    def getSyncModule(self):
        return self.__dict__["syncModule"]

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, syncName):
        self.__dict__["syncName"] = syncName
        self.updateSyncData()

    def getSyncName(self):
        return self.__dict__["syncName"]

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSave(self, value):
        self.__dict__["save"] = value

    def getSave(self):
        return self.__dict__["save"]

    save = QtCore.Property(bool, getSave, setSave)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Sync()
    # widget.show()
    sys.exit(app.exec_())