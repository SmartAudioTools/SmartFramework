# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync import syncModules
from sys import modules


class SyncData(QtCore.QObject):
    # signaux
    output = QtCore.Signal(object)

    def __init__(self, syncModule, syncName):
        super(SyncData, self).__init__()
        self.syncModule = syncModule
        self.syncName = syncName
        syncModules[self.syncModule]._sendStateSignal.connect(self.sendState)
        self._countReceive = 0
        self._countSend = 0

    def input(self, obj, save=True):
        if save and self.syncModule in modules:
            # vraiment ici qu'il faut stocker ?
            modules[self.syncModule].__dict__[self.syncName] = obj
        self.output.emit(obj)

    def sendState(self):
        if self.syncName in modules[self.syncModule].__dict__:
            self.output.emit(modules[self.syncModule].__dict__[self.syncName])
