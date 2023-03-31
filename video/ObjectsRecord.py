# -*- coding: utf-8 -*-
from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QMessageBox
from SmartFramework.tools.memory import (
    GlobalMemoryStatusEx,
    bytes2human,
    getAvailableDiskSpace,
)
from SmartFramework.tools.process import Process
from SmartFramework.files import (
    addToName,
    joinPath,
    splitPath,
    mainPath,
    removeExistingPathAndCreateFolder,
)
from SmartFramework.string.Speech import Speech
import os
from collections import deque
from time import localtime, strftime
import gc
from SmartFramework.serialize.serializejson import dumps
from sys import getsizeof

KiloOctet = 1024
MegaOctet = 1024**2
debug = True  # False


class ObjectsRecord(QtCore.QObject):

    # constructor ------------

    def __init__(
        self,
        parent=None,
        path=None,
        extension="json",
        useBuffer=False,
        askBeforReplace=True,
        speak=False,
        addDate=False,
        checkMemoryPeriode=75,
        ramSecuritySpace=1000 * MegaOctet,
        discSecuritySpace=MegaOctet,
    ):
        """path is None "%s %s.avi"%(mainName,strftime('%Y-%m-%d_%HH%M_%S', localtime())) will be uses"""

        super(ObjectsRecord, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.path = path
        self.extension = extension
        self.useBuffer = useBuffer
        self.askBeforReplace = askBeforReplace
        self.speak = speak
        self.addDate = addDate
        self.checkMemoryPeriode = checkMemoryPeriode
        self.ramSecuritySpace = ramSecuritySpace
        self.discSecuritySpace = discSecuritySpace

        self._recording = False
        self._speaker = Speech()
        self._process = (
            Process()
        )  #  If pid is omitted current process pid (os.getpid()) is used.

    # signaux ------------

    outStop = QtCore.Signal()
    outStart = QtCore.Signal()
    outStartStop = QtCore.Signal(bool)

    # slots ------------

    @QtCore.Slot()
    def start(self):
        if not self._recording:
            self._i = -1
            if self.path is None:
                directory, mainName, ext = splitPath(mainPath)
                path = joinPath(directory, mainName, self.extension)
            else:
                path = self.path
            if self.addDate:
                path = addToName(path, strftime("_%Y-%m-%d_%HH%M_%S", localtime()))
            if os.path.exists(path) and self.askBeforReplace:
                self.say("file already exist, should I replace it ?")
                box = QMessageBox(
                    QMessageBox.Question,
                    "recording",
                    "%s already exist, should I replace it ?" % path,
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                )
                box.setWindowModality(QtCore.Qt.ApplicationModal)
                box.show()
                box.exec()
                answer = box.result()

                if answer == QMessageBox.Discard:
                    self.outStop.emit()
                    self.outStartStop.emit(False)
                    return
                elif answer == QMessageBox.No:
                    orgin_path = path
                    j = 2
                    while os.path.exists(path):
                        path = addToName(orgin_path, f"_{j}")
                        j += 1

            if getAvailableDiskSpace(path) < self.discSecuritySpace:
                print("Disc is full, no more place for recording")
                self.say("Disc is full, no more place for recording")
                self.outStop.emit()
                self.outStartStop.emit(False)
                QMessageBox.critical(
                    None, "recording", "Disc is full, no more place for recording"
                )  # ,QMessageBox.Ok)
                return

            print("recording " + path)
            # self._buffer = deque(self.bufferTime*self.fps)
            self.say("recording")
            self._recording = True
            # previent un changement de useBuffer pendant enregistrement :
            self._recordingBuffer = self.useBuffer
            # previent un changement de path pendant enregistrement (permet d'avoir meme comportement avec et sans buffer)
            self._recordingPath = path
            self.outStart.emit()
            self.outStartStop.emit(True)

    @QtCore.Slot()
    def stop(self):
        if self._recording:
            print("stop recording")
            self.say("stop")
            self._recording = False
            self.outStop.emit()
            self.outStartStop.emit(False)
            if self._recordingBuffer:
                QtCore.QTimer.singleShot(1, self.saveBuffer)
            elif self._i != -1:  # permet de s'assurer que self.videoWriter existe
                del self.streamWriter

    @QtCore.Slot(bool)
    def startStop(self, b):
        if b:
            self.start()
        else:
            self.stop()

    @QtCore.Slot(object)
    def inObject(self, obj):
        if self._recording:
            # print(".",end = None)
            self._i += 1
            if self._recordingBuffer:
                if not self._i:
                    self._objectSize = self.objectRamSize(obj)
                    if hasattr(self, "fps"):
                        self._buffer = deque(maxlen=int(self.bufferTime * self.fps))
                    else:
                        self._buffer = deque()  # ))
                    # self._buffer = deque(maxlen = self.stileAvailableObjects()) # merdiqeu empèche de réenregistrer directement.
                objSize = getsizeof(obj)
                neededMemory = objSize + self.ramSecuritySpace
                if not (self._i % self.checkMemoryPeriode):
                    self.availableMemory = self._process.getAvailableMemory()
                while self.availableMemory < neededMemory:
                    self.availableMemory += getsizeof(self._buffer.popleft())
                self._buffer.append(obj)
                self.availableMemory -= objSize
            else:
                if not self._i:
                    print(self._recordingPath)
                    removeExistingPathAndCreateFolder(self._recordingPath)
                    self.streamWriter = self.openWriter(self._recordingPath, obj)
                if not (self._i % self.checkMemoryPeriode):
                    self.availableMemory = getAvailableDiskSpace(self._recordingPath)
                writeSize = self.streamWriter.write(
                    obj, self.availableMemory - self.discSecuritySpace
                )  # np.copy(img)
                if writeSize == 0:
                    self.stop()
                    print("Disc is full, stop video recording")
                    QMessageBox.critical(
                        None, "video recording", "Disc is full, stop video recording"
                    )  # ,QMessageBox.Ok)
                    return
                elif (
                    writeSize is not None
                ):  # permet de gerer le cas ou on n'a pas implementé de valeur de retour pour la methode write de self.streamWriter
                    self.availableMemory -= writeSize

    # slot / (futur) properties ------

    @QtCore.Slot(str)
    def setPath(self, path):
        if isinstance(path, str):
            fileName, ext = os.path.splitext(path)
            if ext == "":
                path = fileName + "." + self.extension
        self.__dict__[
            "path"
        ] = path  # utilise cette syntaxe pour ne pas faire de boucle infini quand créera propriété QT dans ma compilation pour Qt Designer

    @QtCore.Slot(bool)
    def setSpeak(self, b):
        self.__dict__["speak"] = b

    @QtCore.Slot(float)
    def setBufferTime(self, time):
        self.__dict__["bufferTime"] = time
        self.setUseBuffer(bool(time))

    @QtCore.Slot(bool)
    def setUseBuffer(self, b):
        self.__dict__["useBuffer"] = b

    @QtCore.Slot(bool)
    def setAddDate(self, b):
        self.__dict__["addDate"] = b

    # methodes ------------------

    def saveBuffer(self):
        print("save buffer")
        # recopie variables en local pour si jamais on commence autre enregistrement en //
        buffer = self._buffer
        recordingPath = self._recordingPath
        # postRecordingArgs = self.getPostRecordingArgs()
        removeExistingPathAndCreateFolder(recordingPath)
        streamWriter = self.openWriter(recordingPath, buffer[0])
        i = 0
        checkMemoryPeriode = self.checkMemoryPeriode
        discSecuritySpace = self.discSecuritySpace
        while len(buffer):
            if not (i % checkMemoryPeriode):
                availableMemory = getAvailableDiskSpace(recordingPath)
            writeSize = streamWriter.write(
                buffer.popleft(), availableMemory - discSecuritySpace
            )
            if writeSize == 0:
                self.stop()
                print("Disc is full, only part of the buffer as been saved")
                QMessageBox.critical(
                    None,
                    "video recording",
                    "Disc is full, only part of the buffer as been saved",
                )  # ,QMessageBox.Ok)
                break
            elif (
                writeSize is not None
            ):  # permet de gerer le cas ou on n'a pas implementé de valeur de retour pour la methode write de self.streamWriter
                self.availableMemory -= writeSize
            QtWidgets.QApplication.instance().processEvents()
        del streamWriter
        print("saved buffer")
        del buffer
        gc.collect()
        if debug:
            print(
                "after cleaning free space : %s"
                % bytes2human(self._process.getAvailableMemory())
            )
            print(
                "after cleaning ullAvailVirtual : %s"
                % bytes2human(GlobalMemoryStatusEx().ullAvailVirtual)
            )

    def openWriter(self, path, obj):
        return JsonWriter(path)

    def say(self, text):
        if self.speak:
            self._speaker.speech(text)

    def setGeometry(
        self, geometry
    ):  # hack pour permetre compilation de SmartFace.ui en attendant d'avoir l'heritage multiples de Qt5 pour pouvoir genere plugin Qt Designer pour FrameRecord.py
        pass


class JsonWriter:
    def __init__(self, path, start="[\n", separator=",\n", end="\n]"):
        self.jsonFile = open(path, "wb", encoding="utf-8", newline="")
        self.jsonFile.write(start)
        self.separator = separator
        self.end = end
        self._first = True

    def write(self, obj, availableMemory=None):
        jsonObj = dumps(obj)
        # self.jsonFile..seek(-len(self.end),2) # va à la fin du fichier
        size = len(self.separator) + len(jsonObj)
        if availableMemory is not None and size > availableMemory:
            return 0
        if not self._first:
            self.jsonFile.write(self.separator)
        else:
            self._first = False
        self.jsonFile.write(jsonObj)
        return size
        # self.jsonFile.write(self.end)

    def __del__(self):
        self.jsonFile.write(self.end)
        self.jsonFile.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ObjectsRecord()
    app.exec_()
