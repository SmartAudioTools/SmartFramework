# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.Sync import Sync


class MenuUI(QtWidgets.QComboBox):
    def __init__(
        self,
        parent=None,
        syncModule="synced",
        syncName="",
        syncSave=True,
        serialize=True,
        item=None,
        items=[],
        **kwargs
    ):
        # les initArgs sont utiles pour avoir des valeure par defaut
        QtWidgets.QComboBox.__init__(self, parent, **kwargs)

        # synchronisation & serialization
        self._sync = Sync(self, syncModule, syncName, syncSave)
        self._sync.output[str].connect(self.setItem)
        self.currentTextChanged.connect(self._sync.input)
        self._serialize = serialize

        # if item is not None :
        self._initItem = item
        # self.setCurrentIndex(-1)
        self.alreadyAddItem = False
        if items:
            self.setItems(items)

        # utilise syntaxe longue pour pouvoir stocker timer dans un attribut et stoper la restoration si on a deserialisé par ailleur
        # QtCore.QTimer.singleShot(0,self.restoreItem)
        self._singleShot = QtCore.QTimer(self)
        self._singleShot.setSingleShot(True)
        self._singleShot.timeout.connect(self.restoreItem)
        self._singleShot.start()
        # self.textHighlighted.connect(self.printHighlighted)# marche pas

    # @QtCore.Slot(str)
    # def printHighlighted(self,highlighted):
    #    print(".",highlighted)

    def restoreItem(self):
        self.setItem(self._initItem)

    @QtCore.Slot(str)
    def addItemWithoutDuplicate(self, item):
        if self.findText(item) == -1:
            self.addItem(item)

    def addItem(self, item):
        QtWidgets.QComboBox.addItem(self, item)
        if not self.alreadyAddItem:
            self.setCurrentIndex(-1)
            # permet de bien s'assurer de renvoyer en sortie l'item meme si le premier de la liste (dont l'index est 0 )
            # en effet le premier .addItem(...) emet un signal correspondant à cet item (dans le vide car en general pas encore connecté)
            # puis si on veut restorer item d'index 0  ,il a déjà été envoyé , donc n'est pas renvoyé .
            self.alreadyAddItem = True

    def setItems(self, items):
        self.clear()
        self.addItems(items)
        self.setMaxVisibleItems(len(items))
        self.setCurrentIndex(-1)
        self.alreadyAddItem = True

    def getItems(self):
        return [self.itemText(searchIndex) for searchIndex in range(self.count())]

    items = QtCore.Property(list, getItems, setItems)

    @QtCore.Slot()
    def nextItem(self):
        self.setCurrentIndex((self.currentIndex() + 1) % self.count())
        # self.activated.emit()

    @QtCore.Slot()
    def prevItem(self):
        self.setCurrentIndex((self.currentIndex() - 1) % self.count())

    @QtCore.Slot(str)
    def setItem(self, text):
        if text is None:
            self.setCurrentIndex(-1)
        else:
            i = self.findText(text)
            self.setCurrentIndex(i)
        self._singleShot.stop()

    def getItem(self):
        return self.currentText()

    item = QtCore.Property(str, getItem, setItem)

    def setSyncModule(self, value):
        self._sync.syncModule = value

    def getSyncModule(self):
        return self._sync.syncModule

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        self._sync.syncName = value
        # print('setSyncName : ' + value)

    def getSyncName(self):
        return self._sync.syncName

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        self._sync.save = value

    def getSyncSave(self):
        return self._sync.save

    syncSave = QtCore.Property(bool, getSyncSave, setSyncSave)

    # serialization

    def setSerialize(self, value):
        self._serialize = value

    def getSerialize(self):
        return self._serialize

    serialize = QtCore.Property(bool, getSerialize, setSerialize)

    def __getstate__(self):
        if self._serialize:
            return {"item": self.currentText()}


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MenuUI()
    widget.addItems(["oui", "non"])
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
