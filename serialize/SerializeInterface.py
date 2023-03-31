# -*- coding: utf-8 -*-
import os
import pickle
from qtpy import QtCore, QtWidgets
from SmartFramework.serialize import (
    serialize_parameters,
    serializePython,
    # serializeAsModule,
    serializeTiny,
    serializejson,
)
from SmartFramework.tools.objects import isQWidget
from SmartFramework.files import mainPath, directory, changeExt, read, write
from sys import modules  # ne pas effacer


class SerializeInterface(QtCore.QObject):
    loaded = QtCore.Signal()
    loading = QtCore.Signal()

    def __init__(
        self,
        parent=None,
        target="self.parent()",
        fileName="",
        saveDefaultWhenClose=True,
        saveLastWhenClose=True,
        loadDefaultWhenOpen=True,
        format="python",
        setAttributes=True,
        filtre="_",
        roundFloat=None,
        space=True,
        readableArrayMaxSize=0,
        keepHashToAvoidRewrite=True,
    ):
        super(SerializeInterface, self).__init__(parent)
        # save parameters
        self.target = target
        self.saveDefaultWhenClose = saveDefaultWhenClose
        self.saveLastWhenClose = saveLastWhenClose
        self.loadDefaultWhenOpen = loadDefaultWhenOpen

        self.setAttributes = setAttributes
        self.filtre = filtre
        self.roundFloat = roundFloat
        self.space = space
        self.readableArrayMaxSize = readableArrayMaxSize
        self.setFormat(format)

        self.keepHashToAvoidRewrite = keepHashToAvoidRewrite
        if (not fileName) and mainPath:
            self.fileName = changeExt(mainPath, "dat")
        else:
            self.fileName = fileName
        self.stringHashs = dict()
        # self.oldstringHash = None
        # self.defaultHash = None
        # self.oldFileName = None
        self.defaultFileName = None
        self._loadingFileName = None

        QtWidgets.QApplication.instance().lastWindowClosed.connect(
            self.lastWindowClosed
        )

        # utilise syntaxe longue pour pouvoir stocker timer dans un attribut et eventuellemnet pouvoir le stoper si il y a des changment des SyncModule dans un objet SmartFramework.sync.Sync
        self._singleShot = QtCore.QTimer(self)
        self._singleShot.setSingleShot(True)
        self._singleShot.timeout.connect(self.lookForloadDefaultWhenOpen)
        self._singleShot.start()
        # QtCore.QTimer.singleShot(0, self.lookForloadDefaultWhenOpen) # on appel pas directement le load , pour si entre temps on veut changer la valeure de loadDefaultWhenOpen (par exemple avec un setloadDefaultWhenOpen)

    # slots ----------------------------------------------------

    @QtCore.Slot(str)
    def setFileName(self, fileName):
        self.__dict__["fileName"] = fileName

    @QtCore.Slot()
    @QtCore.Slot(str)
    def saveLastAndLoad(self, fileName=None):
        """peut poser problème si des chose externe comme l'etat d'un fileSelector doit changer entre les deux"""
        self.save()
        self.load(fileName)

    def dumps(self):
        # serialize_parameters.all_setters = self.setAttributes
        # serialize_parameters.filtre = self.filtre
        # serialize_parameters.round_float = self.roundFloat
        # serialize_parameters.space =
        # serialize_parameters.numpy_array_readable_max_size = self.readableArrayMaxSize
        trueObject = eval(self.target)
        if trueObject is not None:
            if self.format == "python":
                stringOrLines = serializePython.dumps(
                    trueObject,
                    setters=self.setAttributes,
                    attributes_filter=self.filtre,
                    splitLines=True,
                    create_QWidget=False,
                    round_float=self.roundFloat,
                    space=self.space,
                    numpy_array_readable_max_size=self.readableArrayMaxSize,
                    # bytes_compression = None
                )
            # elif self.format == "asModule":
            #    stringOrLines = serializeAsModule.dumps(trueObject,create_QWidget = False)
            # elif self.format == "tiny":
            #    stringOrLines = serializeTiny.dumps(trueObject, create_QWidget=False)
            elif self.format == "json":
                stringOrLines = serializejson.dumps(
                    trueObject,
                    attributes_filter=self.filtre,
                    numpy_array_readable_max_size=self.readableArrayMaxSize,
                )
            elif self.format == "pickle":
                stringOrLines = pickle.dumps(trueObject)
            else:
                raise Exception("format de serialisation inconnu")
            return stringOrLines
        else:
            return None

    @QtCore.Slot()
    @QtCore.Slot(str)
    def save(self, fileName=None):
        if fileName:
            self.fileName = fileName
        else:
            fileName = self.fileName
        stringOrLines = self.dumps()
        if stringOrLines:  # and fileName != self.oldFileName:
            if self.keepHashToAvoidRewrite:
                if isinstance(stringOrLines, list):
                    stringOrLines = "\n".join(stringOrLines)
                stringHash = hash(stringOrLines)
                if stringHash == self.stringHashs.get(fileName):
                    return
            print("save " + fileName)
            folder = directory(fileName)
            if folder != "" and not os.path.isdir(folder):
                print("create the folder : ", folder)
                os.makedirs(folder)
            write(fileName, stringOrLines, encoding=self.encoding)

            # self.oldFileName = fileName
            if self.keepHashToAvoidRewrite:
                self.stringHashs[fileName] = stringHash
            #    self.oldstringHash = stringHash
            #    if fileName == self.defaultFileName:
            #        self.defaultHash = stringHash

    @QtCore.Slot(str)
    def setFormat(self, format):
        self.__dict__[
            "format"
        ] = format  # pour ne pas planter quand sera transformé en propriété pour qtdesigner
        if format == "json":
            self.encoding = "utf_8"
        else:
            self.encoding = "utf_8_sig"

    @QtCore.Slot()
    @QtCore.Slot(str)
    def load(self, fileName=None):
        if self._loadingFileName:
            print(
                'empeche de loader "'
                + str(fileName)
                + '" pendant deserialisation de "'
                + str(self._loadingFileName)
                + '"'
            )
        else:
            if fileName:
                self.fileName = fileName
            else:
                fileName = self.fileName
            if os.path.exists(fileName):
                self._loadingFileName = fileName
                self.loading.emit()
                print("load " + fileName)
                string = read(
                    fileName
                )  # , encoding="utf_8_sig" ne permet pas de lire anciens fichiers dat   # "utf_8_sig" permet de lire à la fois de l'utf_8 et utf_8_sig, on précise l'encoding pour acceler la lecteure des json qui n'ont pas de BOM. On a un problème pour pickle...
                if self.keepHashToAvoidRewrite:
                    stringHash = hash(string)
                    self.stringHashs[fileName] = stringHash
                    # self.oldstringHash = stringHash
                    # if fileName == self.defaultFileName:
                    #    self.defaultHash = stringHash
                # self.oldFileName = fileName
                trueObject = eval(self.target)
                if isQWidget(trueObject):
                    # print(' se contente de restaurer les attributs ')
                    if self.format == "python":
                        serializePython.loads(string, obj=trueObject)
                    # elif self.format == "asModule":
                    #    serializeAsModule.loads(string, existingObject=trueObject)
                    # elif self.format == "tiny":
                    #    serializeTiny.loads(string, obj=trueObject)
                    else:
                        raise Exception(
                            "la serialisation "
                            + self.format
                            + " ne suporte pas encore la deserialization d'objets PyQt"
                        )
                else:
                    if self.format == "python":
                        exec(self.target + "= serializePython.loads(string)")
                    # elif self.format == "asModule":
                    #    exec(self.target + "= serializeAsModule.loads(string)")
                    elif self.format == "tiny":
                        exec(self.target + "= serializeTiny.loads(string)")
                    elif self.format == "json":
                        exec(self.target + "= serializejson.loads(string)")
                    elif self.format == "pickle":
                        exec(self.target + "= pickle.loads(string)")
                # print('loaded  ' + self._loadingFileName)

                self._loadingFileName = None
                self.loaded.emit()
            else:
                print("unable to find " + fileName)

    # private -----------------

    def lookForloadDefaultWhenOpen(self):
        self.defaultFileName = self.fileName
        if self.loadDefaultWhenOpen and os.path.exists(self.fileName):
            self.load()

    def lastWindowClosed(self):
        QtWidgets.QApplication.instance().lastWindowClosed.disconnect(
            self.lastWindowClosed
        )
        if self.saveLastWhenClose or self.saveDefaultWhenClose:
            stringOrLines = self.dumps()
            if stringOrLines:
                if self.keepHashToAvoidRewrite:
                    if isinstance(stringOrLines, list):
                        stringOrLines = "\n".join(stringOrLines)
                    stringHash = hash(stringOrLines)
                if self.saveDefaultWhenClose:
                    if (
                        not self.keepHashToAvoidRewrite
                        or (self.defaultFileName not in self.stringHashs)
                        or (stringHash != self.stringHashs[self.defaultFileName])
                    ):
                        print("save " + str(self.defaultFileName))
                        write(
                            self.defaultFileName, stringOrLines, encoding=self.encoding
                        )
                if (
                    self.saveLastWhenClose
                    and self.fileName
                    and self.fileName != self.defaultFileName
                ):
                    if (
                        not self.keepHashToAvoidRewrite
                        or stringHash != self.stringHashs[self.fileName]
                    ):
                        print("save " + self.fileName)
                        write(self.fileName, stringOrLines, encoding=self.encoding)

    def __getstate__(self):
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = SerializeInterface()
    # widget.show()
    sys.exit(app.exec_())
