from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QFileDialog
from SmartFramework.files import splitPath


class FileDialog(QtCore.QObject):
    # path du fichier selectionné 'dossier/nomFile.extension'
    selectPath = QtCore.Signal(str)
    outputFileName = QtCore.Signal(
        str
    )  # sort le nom du dernier file selectionné => permet de sauver le dernier file selectionnéet  (avec un save exterieure) '''

    def __init__(
        self,
        parent=None,
        title="Open File",
        root="",
        filter="All Files (*.*)",
        save=False,
    ):
        super(FileDialog, self).__init__(parent)
        self.title = title
        self.root = root
        self.filter = filter
        self.save = save
        self.__dict__["path"] = ""

    @QtCore.Slot()
    def open(self):
        # print("root : ", self.root)
        if self.path:
            initPath = self.path
        else:
            initPath = self.root
        if self.filter == "*..":
            path = QFileDialog.getExistingDirectory(self.parent(), self.title, initPath)
        elif self.save:
            path, filter = QFileDialog.getSaveFileName(
                self.parent(), self.title, initPath, self.filter
            )  # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner
        else:
            path, filter = QFileDialog.getOpenFileName(
                self.parent(), self.title, initPath, self.filter
            )  # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner
        if path:
            self.setPath(path)

    @QtCore.Slot(str)
    def setPath(self, path):
        self.__dict__["path"] = path
        self.selectPath.emit(path)
        directory, name, ext = splitPath(path)
        self.outputFileName.emit(name)

    def getPath(self):
        return self.__dict__["path"]

    path = QtCore.Property(str, getPath, setPath)

    """
    @QtCore.Slot(str)                    
    def setType(self,path):
        self.__dict__['type'] = path    
    def getType(self):
        return self.__dict__['type']
    type = QtCore.Property(str, getType, setType)
    """

    @QtCore.Slot(bool)
    def setSave(self, path):
        self.__dict__["save"] = path

    def getSave(self):
        return self.__dict__["save"]

    save = QtCore.Property(bool, getSave, setSave)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = FileDialog()
    # widget.show()
    app.exec_()
