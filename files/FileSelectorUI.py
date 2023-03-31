import os
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.files import splitPath
from SmartFramework.files.editableRadioButtonUI import EditableRadioButtonUI
from SmartFramework.sync.syncObjectUI import SyncObjectUI


class FileSelectorUI(SyncObjectUI):

    # path du fichier selectionné 'dossier/nomFile.extension':
    selectPath = QtCore.Signal(str)
    oldPath = QtCore.Signal(str)  # path de l'ancien fichier
    createAndSelectPath = QtCore.Signal(str)  # path de fichier à créer
    # sort le nom du dernier file selectionné => permet de sauver le dernier file selectionnéet  (avec un save exterieure) ''':
    outputFileName = QtCore.Signal(str)

    def __init__(
        self,
        parent=None,
        nombreFiles=4,
        dossierFiles="files",
        extension="dat",
        sendOldPathWhenCreate=False,
        antiFeedback=True,
    ):

        # synchronisation (pas vraiment utile ? )
        SyncObjectUI.__init__(self, parent)
        self.outputFileName.connect(self._sync.input)
        self._sync.output[str].connect(self.setFile)

        # copie des parametre dans at
        self.nombreFiles = nombreFiles
        self.dossierFiles = dossierFiles
        self.extension = extension
        self.sendOldPathWhenCreate = sendOldPathWhenCreate
        self.antiFeedback = antiFeedback

        # recupère tout les nom de fichier correspondant à des files (dans le dossierFiles et finissant par extension)
        self.fileSelected = ""

        if not dossierFiles:
            dossierFiles = "."

        if os.path.exists(dossierFiles):
            if os.path.isdir(dossierFiles):
                listeFichiers = os.listdir(dossierFiles)
                listeFichiersFiles = []
                for fichier in listeFichiers:
                    directory, filename, ext = splitPath(fichier)
                    if ext == extension:
                        listeFichiersFiles.append(filename)
                # trie les fichiers par ordre alphabetique :
                listeFichiersFiles.sort()
                nombreFichiersFiles = len(listeFichiersFiles)
            else:
                raise Exception(
                    "essaye de créer un dossier du meme nom qu'un fichier déjà existant"
                )
        else:
            nombreFichiersFiles = 0

        # recrée un  editablesRadioButtonUI  pour chaque fichier

        self.editablesRadioButtonUI = []

        for i in range(nombreFiles):
            self.editablesRadioButtonUI.append(EditableRadioButtonUI(self))
            self.editablesRadioButtonUI[i].setGeometry(QtCore.QRect(0, 30 * i, 400, 30))
            # if i == 0:
            #    self.editablesRadioButtonUI[i].setText('default')
            if i < nombreFichiersFiles:
                self.editablesRadioButtonUI[i].setText(listeFichiersFiles[i])
            else:
                pass
                # preset_text = '' #"preset_" + str(i+1)
            self.editablesRadioButtonUI[i].stringRename.connect(self.renameFile)
            self.editablesRadioButtonUI[i].stringCreate.connect(self.createFile)
            self.editablesRadioButtonUI[i].stringOut.connect(self.selectFile)

        self.resize(300, 30 * nombreFiles)

    def createFile(self, createName):
        if not os.path.exists(self.dossierFiles):
            os.mkdir(self.dossierFiles)
        if self.sendOldPathWhenCreate and self.fileSelected:
            self.oldPath.emit(self.fileNameToPath(self.fileSelected))
        self.fileSelected = createName
        self.createAndSelectPath.emit(self.fileNameToPath(createName))
        self.outputFileName.emit(createName)

    def renameFile(self, createName, oldName):
        if createName != oldName:
            print("renome " + oldName + " -> " + createName)
            oldPath = self.fileNameToPath(oldName)
            createPath = self.fileNameToPath(createName)
            self.fileSelected = createName
            os.rename(oldPath, createPath)

    @QtCore.Slot(str)
    def setFile(self, fileName):
        # print("setFile %s" % fileName)
        """selectionne un file de l'exterieur en fonction de son nom => permet de restaurer le dernier file selectionnéet  (avec un save exterieure)"""
        if fileName and (fileName != self.fileSelected or not self.antiFeedback):
            # peut servir à empecher feedback notament quand sert à restaurer des sauvegarde qui vont voulaire faire setFile
            for radioButton in self.editablesRadioButtonUI:
                if radioButton.text == fileName:
                    radioButton.click()
                    break
            else:
                if self.editablesRadioButtonUI[0].text:
                    # permet de ne rien selectionner si aucun fichier
                    # permet de selectionner premier file si on a efface le dernier selectionne        :
                    self.editablesRadioButtonUI[0].click()

    def getFile(self):
        return self.fileSelected

    file = QtCore.Property(str, getFile, setFile)

    def fileNameToPath(self, fileName):
        """transforme 'nomFile' en 'dossier/nomFile.extension'"""
        # print('sort  : ' + fileName)
        return self.dossierFiles + "/" + fileName + "." + self.extension

    def selectFile(self, fileName):
        # print("selectFile %s" % fileName)
        if self.fileSelected:
            self.oldPath.emit(self.fileNameToPath(self.fileSelected))
        self.fileSelected = fileName
        self.selectPath.emit(self.fileNameToPath(fileName))
        self.outputFileName.emit(fileName)

    def sizeHint(self):
        return self.size()

    def __getstate__(self):
        if self.fileSelected != None:
            return {"file": self.fileSelected}
        else:
            pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = FileSelectorUI()
    widget.show()
    app.exec_()
