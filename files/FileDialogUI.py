from qtpy import QtCore, QtWidgets
from SmartFramework.files import mainPath, directory, joinPath
import os


class FileDialogUI(QtWidgets.QTreeView):
    selectedPath = QtCore.Signal(str)
    currentPath = QtCore.Signal(str)
    # selectedFileName = QtCore.Signal(str)

    def __init__(self, parent=None, rootPath=None, path=None, ext=None):
        self._initialized = False
        QtWidgets.QTreeView.__init__(self, parent=parent)
        self._model = QtWidgets.QFileSystemModel(self)
        self._model.setResolveSymlinks(True)
        # pour afficher dossier au dessus des fichiers
        self._proxy = MySortFilterProxyModel(self)
        self._proxy.setSourceModel(self._model)
        self.setModel(self._proxy)
        header = self.header()
        header.setSortIndicator(0, QtCore.Qt.AscendingOrder)
        self._proxy.sort(header.sortIndicatorSection(), header.sortIndicatorOrder())
        self.setRootPath(rootPath)
        self.__dict__["path"] = path
        self.setExt(ext)
        header.close()
        for i in range(1, self._model.columnCount()):
            self.setColumnHidden(i, True)
        self.activated.connect(self.emitSelectedPath)
        self._initialized = True
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    @QtCore.Slot(str)
    def setPath(self, path=None):
        if path:
            index = self._proxy.mapFromSource(self._model.index(path))
            self.setCurrentIndex(index)

    def getPath(self):
        return self.__dict__["path"]

    path = QtCore.Property(str, getPath, setPath)

    @QtCore.Slot(str)
    def setRootPath(self, rootPath=None):
        self.__dict__["rootPath"] = rootPath
        if rootPath is None:
            self.setRootIndex(self._proxy.mapFromSource(self._model.index(None)))
            self._model.setRootPath(QtCore.QDir.rootPath())
        elif os.path.isabs(rootPath):
            self.setRootIndex(self._proxy.mapFromSource(self._model.index(rootPath)))
            self._model.setRootPath(rootPath)
        elif mainPath is not None:
            absolutPath = joinPath(directory(mainPath), rootPath)
            self.setRootIndex(self._proxy.mapFromSource(self._model.index(absolutPath)))
            self._model.setRootPath(absolutPath)

    def getRootPath(self):
        return self.__dict__["rootPath"]

    rootPath = QtCore.Property(str, getRootPath, setRootPath)

    @QtCore.Slot(str)
    @QtCore.Slot(object)
    def setExt(self, ext=None):
        if ext is None:
            self._model.setNameFilterDisables(True)
            self.exts = []
        else:
            if isinstance(ext, str):
                ext.replace(" ", ",")
                self.exts = [e.strip("*").strip(".") for e in ext.split(",")]
            else:
                self.exts = ext
            stars = tuple("*." + ext for ext in self.exts)
            self._model.setNameFilterDisables(False)
            self._model.setNameFilters(stars)

    def getExt(self):
        return ",".join(("*." + ext for ext in self.exts))

    ext = QtCore.Property(str, getExt, setExt)

    def emitSelectedPath(self, index):
        path = self.filteredPathFromIndex(index)
        if path is not None:
            self.selectedPath.emit(path)

    def currentChanged(self, index, previous):
        # pas sur que cerve mais le met quand même
        QtWidgets.QTreeView.currentChanged(self, index, previous)
        if self._initialized:
            path = self.filteredPathFromIndex(index)
            if path is not None:
                self.currentPath.emit(path)
                self.__dict__["path"] = path

    def filteredPathFromIndex(self, index):
        fileInfo = self._model.fileInfo(self._proxy.mapToSource(index))
        if not self.exts or fileInfo.isFile():
            return fileInfo.filePath()

    @QtCore.Slot()
    def selectNext(self, loop_folder=False):
        currentIndex = self.currentIndex()
        if loop_folder:
            next_index = currentIndex.siblingAtRow(currentIndex.row() + 1)
            while not self._model.fileInfo(
                self._proxy.mapToSource(next_index)
            ).isFile():
                next_index = currentIndex.siblingAtRow(next_index.row() + 1)
            # self.selectionModel().select(next_index,QtCore.QItemSelectionModel.ClearAndSelect)

            self.setCurrentIndex(next_index)
        else:
            already_all_scanned = False
            next_index = self.indexBelow(currentIndex)
            while not self._model.fileInfo(
                self._proxy.mapToSource(next_index)
            ).isFile():
                if next_index.row() == -1:
                    if already_all_scanned:
                        return  # shoud stop
                    already_all_scanned = True
                    next_index = self.indexBelow(self.rootIndex())
                else:
                    next_index = self.indexBelow(next_index)
            self.setCurrentIndex(next_index)

    @QtCore.Slot()
    def selectPrev(self, loop_folder=False):
        if loop_folder:
            currentIndex = self.currentIndex()
            next_index = currentIndex.siblingAtRow(currentIndex.row() - 1)
            while not self._model.fileInfo(
                self._proxy.mapToSource(next_index)
            ).isFile():
                next_index = currentIndex.siblingAtRow(next_index.row() - 1)
            # self.selectionModel().select(next_index,QtCore.QItemSelectionModel.ClearAndSelect)
            self.setCurrentIndex(next_index)
        else:
            already_all_scanned = False
            currentIndex = self.currentIndex()
            next_index = self.indexAbove(currentIndex)
            while not self._model.fileInfo(
                self._proxy.mapToSource(next_index)
            ).isFile():
                if next_index.row() == -1:
                    if already_all_scanned:
                        return
                    already_all_scanned = True
                    # search last visible file
                    search_last = self.indexBelow(self.rootIndex())
                    last = None
                    while search_last.row() != -1:
                        if self._model.fileInfo(
                            self._proxy.mapToSource(search_last)
                        ).isFile():
                            last = search_last
                        search_last = self.indexBelow(search_last)
                    if last is None:
                        return  # shouldStop
                    next_index = last
                else:
                    next_index = self.indexAbove(next_index)
            self.setCurrentIndex(next_index)


# https://stackoverflow.com/questions/10789284/qfilesystemmodel-sorting-dirsfirst
class MySortFilterProxyModel(QtCore.QSortFilterProxyModel):
    #
    def lessThan(self, left, right):
        if self.sortColumn() == 0:
            fsm = self.sourceModel()
            if self.sortOrder() == QtCore.Qt.AscendingOrder:
                asc = True
            else:
                asc = False
            leftFileInfo = fsm.fileInfo(left)
            rightFileInfo = fsm.fileInfo(right)
            leftFileName = fsm.data(left)
            rightFileName = fsm.data(right)
            # If DotAndDot move in the beginning
            if leftFileName == "..":
                return asc
            if rightFileName == "..":
                return not asc
            # Move dirs upper
            if not leftFileInfo.isDir() and rightFileInfo.isDir():
                return not asc
            if leftFileInfo.isDir() and not rightFileInfo.isDir():
                return asc
            # sort drives
            if leftFileName.find(":") != -1 or rightFileName.find(":") != -1:
                return asc is (leftFileInfo.filePath() < rightFileInfo.filePath())
        return QtCore.QSortFilterProxyModel.lessThan(self, left, right)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = FileDialogUI()
    widget.show()
    app.exec_()
