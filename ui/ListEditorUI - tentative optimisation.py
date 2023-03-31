from qtpy import QtCore, QtWidgets, QtGui
from SmartFramework.serialize import serializeTxt, serializejson
from SmartFramework.files import ext
from qtpy.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QListWidgetItem


class ListEditorUI(QtWidgets.QListWidget):

    # listChanged = QtCore.Signal(object)
    itemsTodo = QtCore.Signal(object)
    itemDoubleClicked = QtCore.Signal(str)
    itemEntered = QtCore.Signal(str)

    def __init__(self, parent=None):
        QtWidgets.QListWidget.__init__(self, parent)
        self.setAcceptDrops(True)
        self._gray = QtGui.QColor(0, 0, 0, 80)
        # self.itemDoubleClicked[QListWidgetItem].connect(self.itemDoubleClickedToStr)
        # self.itemEntered[QListWidgetItem].connect(self.itemEnteredToStr)
        self._filter = "Text Files (*.txt)"
        self.lastPath = None

        self.itemsTexts = []
        self.itemsStates = []
        self.itemsSet = set()

    @QtCore.Slot()
    def load(self):
        # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner         :
        paths, filter = QFileDialog.getOpenFileNames(
            self, "Open list", self.lastPath, self._filter
        )
        if paths:
            self.loadPath(paths[0])
        if len(paths) > 1:
            for path in paths[1:]:
                self.addPath(path)

    @QtCore.Slot(str)
    def loadPath(self, path):
        self.setItems(self.itemsFromPath(path))

    @QtCore.Slot(list)
    @QtCore.Slot(object)
    def setItems(self, items, removeDuplicate=True):
        if removeDuplicate:
            # https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists        :
            items = list(dict.fromkeys(items))
        self.itemsTexts = items
        self.itemsStates = [True] * len(items)
        QtWidgets.QListWidget.clear(self)
        QtWidgets.QListWidget.addItems(self, items)

        # self.listChanged.emit(items)
        self.itemsTodo.emit(self.getItemsTodo())

    @QtCore.Slot()
    def add(self):
        # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner         :
        paths, filter = QFileDialog.getOpenFileNames(
            self, "Add list", self.lastPath, self._filter
        )
        for path in paths:
            self.addPath(path)

    @QtCore.Slot(str)
    def addPath(self, path):
        self.addItems(self.itemsFromPath(path))

    @QtCore.Slot(object)
    def addItems(self, items, removeDuplicate=True):
        self_itemsSet = self.itemsSet
        if removeDuplicate:
            newItems = [item for item in items if item not in self_itemsSet]
            # newItems = [ item for item in items if not QtWidgets.QListWidget.findItems(self,item,QtCore.Qt.MatchExactly)]
        self.itemsSet.update(newItems)
        self.itemsTexts += newItems
        self.itemsState += [True] * len(newItems)
        QtWidgets.QListWidget.addItems(self, newItems)
        self.itemsTodo.emit(self.getItemsTodo())

    @QtCore.Slot()
    def subtract(self):
        # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner            :
        paths, filter = QFileDialog.getOpenFileNames(
            self, "Subtract list", self.lastPath, self._filter
        )
        for path in paths:
            self.subtractPath(path)

    @QtCore.Slot(str)
    def subtractPath(self, path):
        self.subtractItems(self.itemsFromPath(path))

    def subtractItems(self, items):
        itemsSet = set(items)
        itemsToRemove = itemsSet.intersection(self.self.itemsSet)
        for i in range(self.count() - 1, -1, -1):
            if self.itemsTexts[i] in itemsToRemove:
                self.takeItem(i)
        self.itemsTodo.emit(self.getItemsTodo())

    @QtCore.Slot()
    def intersection(self):
        # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner            :
        paths, filter = QFileDialog.getOpenFileNames(
            self, "Intesection with list", self.lastPath, self._filter
        )
        for path in paths:
            self.intersectionPath(path)

    @QtCore.Slot(str)
    def intersectionPath(self, path):
        self.intersectionItems(self.itemsFromPath(path))

    def intersectionItems(self, items):
        itemsToRemove = self.itemsSet.difference(items)
        for i in range(self.count() - 1, -1, -1):
            if self.itemsText[i] in itemsToRemove:
                self.takeItem(i)
        self.itemsTodo.emit(self.getItemsTodo())

    @QtCore.Slot()
    def dump(self):
        # eviter d'ecrire QtWidgets.QFileDialog pour pas que merde pour compilation -> QtDesigner            :
        path, filter = QFileDialog.getSaveFileName(
            self, "Save list", self.lastPath, self._filter
        )
        self.dumpPath(path)

    @QtCore.Slot(str)
    def dumpPath(self, path):
        if ext(path) == "txt":
            serializeTxt.dump(self.getItems(), path)
        if ext(path) == "json":
            serializejson.dump(self.getItems(), path)
        self.lastPath = path

    def __getstate__(self):
        state = {"items": self.getItems(), "itemsDone": self.getItemsDone()}
        if self.lastPath:
            state["lastPath"] = self.lastPath
        return state

    def itemsFromPath(self, path):
        if ext(path) == "txt":
            items = serializeTxt.load(path)
        if ext(path) == "json":
            items = serializejson.load(path)
        self.lastPath = path
        return items

    def getItems(self):
        return self.itemsText  # [self.item(i).text() for i in range(self.count())]

    def setItemsDone(self, names):
        for name in names:
            items = QtWidgets.QListWidget.findItems(self, name, QtCore.Qt.MatchExactly)
            for item in items:
                item.setForeground(self._gray)
        self.itemsTodo.emit(self.getItemsTodo())

    @QtCore.Slot(str)
    def setItemDone(self, name):
        items = QtWidgets.QListWidget.findItems(self, name, QtCore.Qt.MatchExactly)
        for item in items:
            item.setForeground(self._gray)

    # self.itemsTodo.emit(self.getItemsTodo()) # je le comment pour ne pas recommence à essayer d'envoyer des messages à ceux qu'il a sauté dans SmartRobot

    def getItemsTodo(self):
        return [
            self.item(i).text()
            for i in range(self.count())
            if self.item(i).foreground().color() != self._gray
        ]

    def getItemsDone(self):
        return [
            self.item(i).text()
            for i in range(self.count())
            if self.item(i).foreground().color() == self._gray
        ]

    def mouseDoubleClickEvent(self, event):
        self.itemDoubleClicked.emit(self.item(self.currentRow()).text())

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete):
            self.takeItem(self.currentRow())
            self.itemsTodo.emit(self.getItemsTodo())
        else:
            QtWidgets.QListWidget.keyPressEvent(self, event)
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                self.itemEntered.emit(self.item(self.currentRow()).text())

    def dragMoveEvent(self, event):  # besoin pour QListWidget !?
        event.accept()

    def dragEnterEvent(self, event):
        print("drag enter")
        event.accept()

    def dropEvent(self, event):
        event.accept()
        print("dropEvent")
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            QtCore.QTimer.singleShot(0, lambda: self.addPath(path))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ListEditorUI()
    # widget.setItems(["martin","baptiste","remi"])
    # widget.setItemsDone(["martin"])
    widget.show()
    app.exec_()
