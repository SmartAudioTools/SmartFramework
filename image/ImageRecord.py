from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QMessageBox
import cv2
import os
from SmartFramework.files import directory, addToName
import numpy


class ImageRecord(QtCore.QObject):
    # constructor ------------

    def __init__(
        self, parent=None, path="image.png", askBeforReplace=True, incPath=True
    ):
        super(ImageRecord, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.path = path
        self.askBeforReplace = askBeforReplace
        self.incPath = incPath
        self._nbImages = 5
        self._images = []

    # signaux ------------

    # slots ------------

    @QtCore.Slot()
    def snapshot(self):
        newPath = self.path
        if os.path.exists(self.path):
            if self.incPath:
                num = 2
                newPath = addToName(self.path, "_" + str(num))
                while os.path.exists(newPath):
                    num += 1
                    newPath = addToName(self.path, "_" + str(num))

            elif self.askBeforReplace:
                replace = (
                    QMessageBox.question(
                        None,
                        "Image file ",
                        "%s already exist, should I replace it ?" % self.path,
                        QMessageBox.Yes,
                        QMessageBox.No,
                    )
                    == QMessageBox.Yes
                )
                if not replace:
                    return

        if len(self.path) > 256:
            print("le path dépasse 256 characteres,impossible d'enregistrer l'image")
        else:
            print("save " + newPath)
            folder = directory(newPath)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            sumImage = numpy.zeros(self._image.shape, dtype=int)
            for image in self._images:
                sumImage = sumImage + image
            meanImage = (sumImage / len(self._images)).astype(numpy.uint8)
            print(len(self._images))
            cv2.imwrite(newPath, meanImage)

    @QtCore.Slot(object)
    def inImage(self, image):
        self._image = image
        self._images.append(image)
        if len(self._images) > self._nbImages:
            del self._images[0]

    # slot / (futur) properties ------

    @QtCore.Slot(str)
    def setPath(self, path):
        fileName, ext = os.path.splitext(path)
        if ext == "":
            path = fileName + ".png"
        self.__dict__[
            "path"
        ] = path  # utilise cette syntaxe pour ne pas faire de boucle infini quand créera propriété QT dans ma compilation pour Qt Designer


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoRecord()
    app.exec_()
