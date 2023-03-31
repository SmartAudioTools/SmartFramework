# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets


class CyclicalComboBoxUI(QtWidgets.QComboBox):
    def __init__(
        self, parent=None, serialize=True, alignment=QtCore.Qt.AlignLeft, items=[]
    ):
        # les initArgs sont utiles pour avoir des valeure par defaut
        QtWidgets.QComboBox.__init__(self, parent)
        self._serialize = serialize
        self.setEditable(True)
        self._lineEdit = self.lineEdit()
        self._lineEdit.setReadOnly(True)
        # permet ouverture popup quand clique sur widget      :
        self._lineEdit.installEventFilter(self)
        self.setAlignment(alignment)
        self._showedPopup = False
        self._HiddenItem = None
        self._alreadyAddItem = False
        # self.children()[2].resize(0,0)

        # ne marche pas :
        self.setStyleSheet(
            """QComboBox::drop-down{border: 0px}QComboBox::down-arrow {image: url(noimg)} """
        )
        if items:
            self.setItems(items)
        # self.setStyleSheet("""QWidget{color:white;selection-color:black;background-color:black;selection-background-color:white;}QComboBox::down-arrow {image: url(noimg)} """) #ne marche pas
        # self.view().setAlignment(QtCore.Qt.AlignHCenter)
        # self.setLayoutDirection(QtCore.Qt.RightToLeft)

    def showPopup(self):
        self._showedPopup = True
        self._HiddenItem = self.currentIndex()
        self.view().setRowHidden(self._HiddenItem, True)
        QtWidgets.QComboBox.showPopup(self)

    def hidePopup(self):
        if self._HiddenItem is not None:
            self.view().setRowHidden(self._HiddenItem, False)
            self._HiddenItem = None
        QtWidgets.QComboBox.hidePopup(self)
        self._showedPopup = False

    def eventFilter(self, obj, event):
        """Function to filter out the unwanted events and add new functionalities for it."""
        eventType = event.type()
        if obj == self._lineEdit:
            if eventType == QtCore.QEvent.MouseButtonDblClick:
                # empeche la selection de text dans lineedit par double click:
                return True
            if eventType == QtCore.QEvent.MouseButtonRelease:
                self.nextItem()
                return True
            if (
                eventType == QtCore.QEvent.MouseMove
                and event.buttons()
                and not self._showedPopup
            ):
                self.showPopup()
        return False

    @QtCore.Slot(object)
    def setItems(self, items):
        self.clear()
        self.addItems(items)

    def getItems(self):
        return [self.itemText(searchIndex) for searchIndex in range(self.count())]

    items = QtCore.Property(list, getItems, setItems)

    @QtCore.Slot(str)
    def addItemWithoutDuplicate(self, item):
        if self.findText(item) == -1:
            self.addItem(item)

    @QtCore.Slot(str)
    def addItem(self, item):
        QtWidgets.QComboBox.addItem(self, item)
        # self.setItemData(self.findText(item) ,QtCore.Qt.AlignHCenter) ne marche pas
        if not self._alreadyAddItem:
            self.setCurrentIndex(-1)
            # permet de bien s'assurer de renvoyer en sortie l'item meme si le premier de la liste (dont l'index est 0 )
            # en effet le premier .addItem(...) emet un signal correspondant à cet item (dans le vide car en general pas encore connecté)
            # puis si on veut restorer item d'index 0  ,il a déjà été envoyé , donc n'est pas renvoyé .
            self._alreadyAddItem = True

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
        # self._singleShot.stop()

    def getItem(self):
        return self.currentText()

    item = QtCore.Property(str, getItem, setItem)

    def setAlignment(self, alignment):
        self._lineEdit.setAlignment(alignment)

    def getAlignment(self):
        return self._lineEdit.alignment()

    alignment = QtCore.Property(QtCore.Qt.AlignmentFlag, getAlignment, setAlignment)

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
    app.setStyle("Plastique")
    widget = CyclicalComboBoxUI()
    widget.addItems(["oui", "non"])
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
