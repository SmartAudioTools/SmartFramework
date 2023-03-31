from qtpy import QtCore, QtGui, QtWidgets
import cv2
import os
import numpy as np


class VideoBuffer(QtCore.QObject):
    # constructor ------------

    def __init__(self, parent=None, path="videoRec.avi", codec="LAGS", fps=30):
        super(VideoBuffer, self).__init__(parent)
        self.path = path
        self.codec = codec
        self.fps = fps
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self._recording = False
        self.imageBuffer = []

    # signaux ------------

    # slots ------------

    @QtCore.Slot()
    def recStart(self):
        if not self._recording:
            self.imageBuffer = []
            self._recording = True

    @QtCore.Slot()
    def recStop(self):
        if self._recording:
            self._recording = False

    @QtCore.Slot(bool)
    def recStartStop(self, b):
        if b:
            self.recStart()
        else:
            self.recStop()

    @QtCore.Slot(object)
    def inImage(self, img):
        if self._recording:
            self.imageBuffer.append(img)

    # slot / (futur) properties ------

    @QtCore.Slot(float)
    def setFps(self, value):
        self.__dict__[
            "fps"
        ] = value  # utilise cette syntaxe pour ne pas faire de boucle infini quand créera propriété QT dans ma compilation poru Qt Designer

    @QtCore.Slot(str)
    def setPath(self, fileName):
        name, ext = os.path.splitext(fileName)
        if ext == "":
            fileName = name + ".avi"
        self.__dict__[
            "path"
        ] = fileName  # utilise cette syntaxe pour ne pas faire de boucle infini quand créera propriété QT dans ma compilation pour Qt Designer

    @QtCore.Slot(str)
    def setCodec(self, value):
        self.__dict__["codec"] = value

    @QtCore.Slot()
    def save(self):
        self.openWriter(self.imageBuffer[0], self.path)
        for img in self.imageBuffer:
            self.videoWriter.write(np.copy(img))
        del self.videoWriter

    @QtCore.Slot(str)
    def saveFile(self, fileName):
        name, ext = os.path.splitext(fileName)
        if ext == None:
            fileName = name + ".avi"
        self.__dict__["path"] = fileName
        self.save()

    # methodes ------------------

    def openWriter(self, img, path):
        if os.path.exists(path):
            os.remove(path)
        self.videoWriter = cv2.VideoWriter()
        shape = img.shape
        size = (shape[1], shape[0])
        if len(shape) > 2 or (
            self.codec == "LAGS"
        ):  # B&N NE MARCE PAS avec LAGS !!!! enregistre fichier vide !!!
            isColor = True
        else:
            isColor = False
        retval = self.videoWriter.open(path, self.fourcc(), self.fps, size, isColor)
        if not retval:
            if self.codec == "LAGS" and cv2.__version__ > "3.4.3":
                raise Exception(
                    "Open CV ne supporte plus le codec LAGS en ecriture après la version 3.4.3"
                )
            raise Exception(
                "Impossible d'ouvrire le fichier video %s en ecriture , verifiez que le codec est installe"
                % self.recPath
            )

    def fourcc(self):
        if self.codec == "Menu":
            return -1
        else:
            return cv2.VideoWriter_fourcc(*str(self.codec))


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoBuffer()
    app.exec_()
