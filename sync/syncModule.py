# -*- coding: utf-8 -*-
import types
from qtpy import QtCore
from SmartFramework.serialize.SerializeInterface import SerializeInterface
from sys import modules
from SmartFramework.files import mainName


class SyncModule(QtCore.QObject):
    _sendStateSignal = QtCore.Signal()

    """
    def __setattr__(self, name, value):
        if hasattr(self,name) :
            self.__dict__[name].input(value)
        else : 
            self.__dict__[name] = value 
        #permet de pouvoir faire des assignation  sur saveMIror qui envoir de la synchro ??
    """

    def __init__(self, parent=None, syncModule="synced"):
        super(SyncModule, self).__init__( parent)
        modules[syncModule] = types.ModuleType(syncModule)
        if mainName:
            if syncModule == "synced":
                defaultFileName = mainName + ".sync"
            else:
                defaultFileName = mainName + "_" + syncModule + ".sync"
        else:
            defaultFileName = ""
        self._serialize = SerializeInterface(
            self,
            target="modules['" + syncModule + "']",
            fileName=defaultFileName,
            saveDefaultWhenClose=False,  # A REVOIR ! empeche sauvegarde
            saveLastWhenClose=False,  # A REVOIR ! empeche sauvegarde
            loadDefaultWhenOpen=False,  # A REVOIR ! empeche sauvegarde
            format="python",
        )
        self._serialize.loaded.connect(self._sendState)

    def _sendState(self):
        self._sendStateSignal.emit()

    def __getstate__(self):
        pass
