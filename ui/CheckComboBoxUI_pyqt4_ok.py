# -*- coding: utf-8 -*-
"""
    Autor : Baptiste de La Gorce
    Description : PyQt4 custom combobox for selecting multiple options.
    Created : OCt 14, 2016
    Email : baptiste.delagorce@smartaudiotools.com
"""
from PyQt4 import QtGui, QtCore
import collections

# from SmartFramework.sync.syncObjectUI import Sync


from SmartFramework.tools.dictionaries import reverseDict

eventNames = reverseDict(QtCore.QEvent.__dict__)


class CheckComboBoxUI(QtGui.QComboBox):

    checkedItems = QtCore.pyqtSignal(object)
    checkedItemsAndColors = QtCore.pyqtSignal(object)
    itemsStateAndColors = QtCore.pyqtSignal(object)
    # checkedItemIndexs  = QtCore.pyqtSignal(object)
    checkedCategorieItemsDict = QtCore.pyqtSignal(object)
    changeColor = QtCore.pyqtSignal(str, object)
    highlightedCategorieItems = QtCore.pyqtSignal(object, str)
    # highlighted      # existe déjà

    def __init__(
        self,
        parent=None,
        syncModule="synced",
        syncName="",
        syncSave=True,
        serialize=True,
    ):
        QtGui.QComboBox.__init__(self, parent)
        self._separator = ","
        self._defaultText = "Select"
        self._selectAllText = "All"
        self._changeColorEnable = True
        self._model = self.model()
        self._lineEdit = QtGui.QLineEdit()
        self._lineEdit.setReadOnly(True)
        self.setLineEdit(self._lineEdit)
        self._listView = self.view()
        # ne pas mettre, empeche emition de highlighted ?:
        self._listView.installEventFilter(self)
        # empeche le popup de se refermer quand click gauche :
        self._listView.viewport().installEventFilter(self)
        # empeche de redeclancher un click sur lineedit qui va immédiatemnet reloader le popup quand on click sur la ligne pour juste fermer le pop :
        self._listView.window().installEventFilter(self)
        # permet ouverture popup quand clique sur widget      :
        self._lineEdit.installEventFilter(self)
        self.installEventFilter(self)
        self.highlighted[int].connect(self.emitHighlightedCategorieItems)
        self.i = 0  # compteur pour affichage des evenement lors de debugage
        self.clear()

        # synchronisation & serialization
        # self._sync = Sync(self, syncModule = syncModule, syncName = syncName, save = syncSave)
        # self.itemsStateAndColors.connect(self._sync.input)
        # self._sync.output[object].connect(self.setItemsStateAndColors)
        self._serialize = serialize

    # @QtCore.pyqtSlot(str)
    def emitHighlightedCategorieItems(self, index):
        itemStr = self.itemText(index)
        for searchIndex in range(index - 1, -1, -1):
            searchItem = self.itemFromIndex(searchIndex)
            if searchItem.isTristate():
                categorie = self.itemText(searchIndex)
                break
        else:
            categorie = None
        self.highlightedCategorieItems.emit(categorie, itemStr)

    @QtCore.pyqtSlot()
    def clear(self):
        # print("checkCombobox clear")
        self._text = self._defaultText
        self._checkedItems = []
        self._checkedItemsAndColors = []
        # self._checkedItemIndexs = []
        self._checkedCategorieItems = collections.OrderedDict()
        QtGui.QComboBox.clear(self)
        self.updatePrintedText()

    def addItems(self, items):
        for item in items:
            self.addItemWithoutDuplicate(item)

    def setItems(self, items):
        if self.count():
            self.clear()
        self.addItems(items)
        self.setMaxVisibleItems(len(items))

    @QtCore.pyqtSlot(str)
    @QtCore.pyqtSlot(object)
    def addItemWithoutDuplicate(self, item, itemChecked=False):
        # ajoute par Baptiste de La Gorce
        self.addItem(item, duplicate=False)

    @QtCore.pyqtSlot(str)
    @QtCore.pyqtSlot(object)
    def addItem(
        self, item, itemChecked=False, categorie=None, isCategorie=False, duplicate=True
    ):
        if not isinstance(item, str):
            itemStr = item.name
            itemChecked = item.state
            categorie = item.categorie
            isCategorie = item.isCategorie
        else:
            itemStr = item
        if isCategorie:
            categorieIndex = self.findText(categorie)
            if categorieIndex == -1:
                self.addCategorie(itemStr, itemChecked)
        else:
            if categorie:
                categorieIndex = self.findText(categorie)
                if categorieIndex == -1:
                    self.addCategorie(categorie, itemChecked)
                    itemIndex = self.count()
                    QtGui.QComboBox.addItem(self, itemStr)
                else:
                    for searchIndex in range(categorieIndex + 1, self.count()):
                        if self._model.item(searchIndex, 0).isTristate():
                            itemIndex = searchIndex
                            self.insertItem(itemIndex, itemStr)
                            break
                        if (self.itemText(searchIndex) == itemStr) and not duplicate:
                            itemIndex = searchIndex
                            break
                    else:
                        itemIndex = self.count()
                        QtGui.QComboBox.addItem(self, itemStr)
            else:
                itemIndex = self.findText(itemStr)
                if duplicate or itemIndex == -1:
                    itemIndex = self.count()
                    QtGui.QComboBox.addItem(self, itemStr)
            itemObj = self._model.item(itemIndex, 0)
            itemObj.setCheckable(True)
            if itemChecked:
                self.toggleCheckStateItem(itemIndex, QtCore.Qt.Checked)
            elif itemIndex == 0:
                # par defaut il met nom premier element rajoute. mis un singleshot car sinon n'arrivais pas a effacer premier element.... (doit y'avoir un repaint qui fou la merde):
                QtCore.QTimer.singleShot(0, self.updateText)

        self.setMaxVisibleItems(self.count())

    def addCategorie(self, categorie, categorieChecked=QtCore.Qt.PartiallyChecked):

        self.addItem(categorie)
        item = self.model().item(self.count() - 1, 0)
        item.setBackground(QtGui.QBrush(QtGui.QColor(220, 220, 220)))
        item.setTristate(True)
        font = QtGui.QFont()
        font.setWeight(QtGui.QFont.DemiBold)
        item.setFont(font)
        item.setCheckState(categorieChecked)

    def __getstate__(self):
        """un peu degeulasse, mais fait le boulot"""
        itemList = []
        for index in range(self.count()):
            item = self.itemFromIndex(index)
            itemList.append(
                ItemCategorieStateColor(
                    name=self.itemText(index),
                    categorie=None,  # pas besoin de sauver
                    state=self.itemData(index, QtCore.Qt.CheckStateRole),
                    color=self.itemData(index, QtCore.Qt.TextColorRole),
                    isCategorie=item.isTristate(),
                )
            )
        return itemList  # {"items" : itemList}

    def __setstate__(self, state):
        """un peu degeulasse, mais fait le boulot"""
        for item in state:  # state["items"]:
            itemIndex = self.findText(item.name)
            if itemIndex == -1:
                self.addItem(item)
            else:
                self.setItemData(itemIndex, item.state, QtCore.Qt.CheckStateRole)
                if item.color:
                    self.setItemData(itemIndex, item.color, QtCore.Qt.TextColorRole)
        self.updateTextAndEmitCheckedItems()

    def setItemsStateAndColors(self, itemsStateAndColors):
        for itemIndex in range(self.count()):
            itemStr = self.itemText(itemIndex)
            if itemStr in itemsStateAndColors:
                state, color = itemsStateAndColors[itemStr]
                self.setItemData(itemIndex, state, QtCore.Qt.CheckStateRole)
                if color is not None:
                    self.setItemData(
                        itemIndex, QtGui.QColor(*color), QtCore.Qt.TextColorRole
                    )
        self.updateTextAndEmitCheckedItems()

    # Propriétés  ----------------------------------------------

    def getDefaultText(self):
        return self._defaultText

    def setDefaultText(self, text):
        self._defaultText = text
        self.updateText()

    defaultText = QtCore.pyqtProperty(str, getDefaultText, setDefaultText)

    def getSelectAllText(self):
        return self._selectAllText

    def setSelectAllText(self, text):
        self._selectAllText = text
        self.updateText()

    selectAllText = QtCore.pyqtProperty(str, getSelectAllText, setSelectAllText)

    def getSeparator(self):
        return self._separator

    def setSeparator(self, separator):
        self._separator = separator
        self.updateText()

    separator = QtCore.pyqtProperty(str, getSeparator, setSeparator)

    def getChangeColorEnable(self):
        return self._changeColorEnable

    def setChangeColorEnable(self, b):
        self._changeColorEnable = b

    changeColorEnable = QtCore.pyqtProperty(
        bool, getChangeColorEnable, setChangeColorEnable
    )

    # Fonction internes  ----------------------------------------------

    def updateTextAndEmitCheckedItems(self):
        """Slot to update the text and emit checkedItems"""
        # print("updateTextAndEmitCheckedItems")
        self.updateCheckedItems()
        self.checkedItems.emit(self._checkedItems)
        self.checkedItemsAndColors.emit(self._checkedItemsAndColors)
        # self.checkedItemIndexs.emit(self._checkedItemIndexs)
        self.checkedCategorieItemsDict.emit(dict(self._checkedCategorieItems))
        self.itemsStateAndColors.emit(self._itemsStateAndColor)

    def updateText(self):
        # ra= rea
        # update self._text
        if not self._checkedCategorieItems:
            self._text = self._defaultText
        # elif len(self._checkedItems) == self._model.rowCount():
        #    self._text = self._selectAllText
        else:
            textElements = []
            for categorie, itemStrs in self._checkedCategorieItems.items():
                if categorie is not None:
                    textElements.append("[%s]" % categorie)
                textElements.append(self._separator.join(itemStrs))
            self._text = " ".join(textElements)
        self.updatePrintedText()

    def updatePrintedText(self):  # appeller par resize et après ajout premier element
        # update printedText
        completText = self._text
        textWidth = QtGui.QFontMetrics(self.font()).boundingRect(completText).width()
        if textWidth <= (self.width() - 30):
            printedText = completText
        else:
            for i in range(len(completText)):
                troncatedText = completText[:i]
                testText = troncatedText + "..."
                textWidth = (
                    QtGui.QFontMetrics(self.font()).boundingRect(testText).width()
                )
                if textWidth > (self.width() - 30):
                    break
                printedText = testText
        # print("updatePrintedText : ",printedText)
        self.setEditText(printedText)

    def reloadPopup(self):
        """Function to reload the popup of the Combobox."""
        # print("reloadPopup")
        # self._reloadingPopup = True
        currentIndex = self._listView.currentIndex()
        scrollValue = self._listView.verticalScrollBar().value()
        # print("showPopup")
        # self.setCurrentIndex(-1)
        # self._listView.setCurrentIndex(QtCore.QModelIndex(-1))
        self.showPopup()  # repaint qui fait clignoter element ?
        # print("setCurrentIndex")
        self._listView.setCurrentIndex(currentIndex)
        # print("verticalScrollBar")
        self._listView.verticalScrollBar().setValue(scrollValue)
        # self._reloadingPopup = False

    def contextMenuEvent(self, event):
        """Function to override defaut contextMenu of lineedit (copy , select all)"""
        pass

    def keyPressEvent(self, event):
        """Function to override key press event.to avoid to select item when use up and down arraw"""
        pass

    def resizeEvent(self, event):
        """permet de metre à jour affichage quand redimensionnemnet"""
        retour = QtGui.QComboBox.resizeEvent(self, event)
        self.updatePrintedText()
        return retour

    def eventFilter(self, obj, event):
        """Function to filter out the unwanted events and add new functionalities for it."""
        eventType = event.type()
        # if (eventType not in [QtCore.QEvent.MouseMove,QtCore.QEvent.DynamicPropertyChange,QtCore.QEvent.UpdateRequest,QtCore.QEvent.Paint,QtCore.QEvent.HoverMove]) and (eventType in eventNames):
        #    self.i+=1
        #    print(self.i , " : ",obj,eventNames[eventType])

        if obj == self:
            if eventType == QtCore.QEvent.KeyPress and event.key() in (
                QtCore.Qt.Key_Up,
                QtCore.Qt.Key_Down,
            ):
                # viré self._listView car reclanché un reloadpopup à chaque appuy de fleches haut-bas, meme si déjà ouvert
                self.reloadPopup()  # permet d'ouvre le popup avec les fleches
                return True

        if obj == self._listView.window():
            if eventType == QtCore.QEvent.MouseButtonPress:
                #  empeche de redeclancher un click sur lineedit qui va immédiatemnet reloader le popup quand on click sur la ligne pour juste fermer le pop :
                return True

        if obj == self._lineEdit:
            if eventType == QtCore.QEvent.MouseButtonDblClick:
                # empeche la selection de text dans lineedit par double click:
                return True
            if eventType == QtCore.QEvent.MouseButtonPress:
                self.reloadPopup()
                return True

        if obj == self._listView.viewport():
            if eventType in [
                QtCore.QEvent.MouseButtonPress,
                QtCore.QEvent.MouseButtonDblClick,
            ]:
                index, item = self.currentIndexAndItem()
                if item.isTristate():
                    if event.button() == QtCore.Qt.RightButton:
                        self.toggleCheckStateAllCategorie(index)
                    else:
                        self.toggleCheckStateCategorie(index)
                else:
                    if (
                        self._changeColorEnable
                        and event.button() == QtCore.Qt.RightButton
                    ):
                        pass
                        # bloque en attendant couleure :
                        color = QtWidgets.QColorDialog.getColor(
                            QtGui.QColor(self.itemData(index, QtCore.Qt.TextColorRole)),
                            self,
                            "chose Color",
                            QtWidgets.QColorDialog.ColorDialogOptions(1),
                        )
                        if color.isValid():
                            self.setItemData(index, color, QtCore.Qt.TextColorRole)
                            self.changeColor.emit(self.itemText(index), color.getRgb())
                            self.updateTextAndEmitCheckedItems()
                        self.reloadPopup()
                    else:
                        # permet de changer etat quand click souris:
                        self.toggleCheckStateItem(index)
                return True
            if eventType == QtCore.QEvent.MouseButtonRelease:
                # if event.button() == QtCore.Qt.LeftButton:
                return True  # empèche le popup de se refermer
        if obj == self._listView:
            if eventType == QtCore.QEvent.Hide:
                self.highlighted[str].emit("")
                self.highlightedCategorieItems.emit(None, None)
            if eventType == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Space:
                    index, item = self.currentIndexAndItem()
                    if item.isTristate():
                        self.toggleCheckStateCategorie(index)
                    else:
                        self.toggleCheckStateItem(index)
                    return True

                if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                    # print("enter ", obj)
                    # empeche de rempalcer text par current element lors du enter :
                    self.updatePrintedText()
                    return True
        return False

    # version complexe ---------------
    def currentIndexAndItem(self):
        QModelIndex = self._listView.currentIndex()
        return QModelIndex.row(), self._model.itemFromIndex(QModelIndex)

    def itemFromIndex(self, index):
        return self._model.item(index, 0)

    def toggleCheckStateAllCategorie(self, index):
        # appellé par click souris mais pas clavier
        value = self.itemData(index, QtCore.Qt.CheckStateRole)
        if value != QtCore.Qt.Checked:
            state = QtCore.Qt.Checked
        else:
            state = QtCore.Qt.Unchecked

        for searchIndex in range(index + 1, self.count()):
            searchItem = self.itemFromIndex(searchIndex)
            if searchItem.isTristate():
                break
            else:
                self.setItemData(searchIndex, state, QtCore.Qt.CheckStateRole)

        self.setItemData(index, state, QtCore.Qt.CheckStateRole)
        self.updateTextAndEmitCheckedItems()

    def toggleCheckStateCategorie(self, index):
        # appellé par click souris et touche "space" du clavier
        value = self.itemData(index, QtCore.Qt.CheckStateRole)
        if value != QtCore.Qt.Unchecked:
            self.setItemData(index, QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
        else:
            # ou cocher juste la categorie avec click gauche souris ou keyspace > passer en s'il le faut PartiallyChecked
            for searchIndex in range(index + 1, self.count()):
                searchItem = self.itemFromIndex(searchIndex)
                if searchItem.isTristate():
                    break
                elif not self.itemData(searchIndex, QtCore.Qt.CheckStateRole):
                    self.setItemData(
                        index, QtCore.Qt.PartiallyChecked, QtCore.Qt.CheckStateRole
                    )
                    self.updateTextAndEmitCheckedItems()
                    return
            self.setItemData(index, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        self.updateTextAndEmitCheckedItems()

    def toggleCheckStateItem(self, index, state=None):
        # appellé par click souris et touche "space" du clavier
        if state is None:
            value = self.itemData(index, QtCore.Qt.CheckStateRole)
            if value:
                state = QtCore.Qt.Unchecked
            else:
                state = QtCore.Qt.Checked
        self.setItemData(index, state, QtCore.Qt.CheckStateRole)
        self.updateCategorieBox(index, state)

    def updateCategorieBox(self, index, state):
        # met à jour la categorie ?
        # print("updateCategorieBox")
        categorieState = state
        categorieIndex = None
        for searchIndex in range(index - 1, -1, -1):
            searchItem = self.itemFromIndex(searchIndex)
            searchValue = self.itemData(searchIndex, QtCore.Qt.CheckStateRole)
            if searchItem.isTristate():
                categorieIndex = searchIndex
                oldCategorieState = searchValue
                break
            if searchValue != state:
                categorieState = QtCore.Qt.PartiallyChecked

        for searchIndex in range(index + 1, self.count()):
            searchItem = self.itemFromIndex(searchIndex)
            searchValue = self.itemData(searchIndex, QtCore.Qt.CheckStateRole)
            if searchItem.isTristate():
                break
            if searchValue != state:
                categorieState = QtCore.Qt.PartiallyChecked
        if categorieIndex is not None:
            if not categorieState:
                categorieState = QtCore.Qt.PartiallyChecked
            if categorieState != oldCategorieState:
                self.setItemData(
                    categorieIndex, categorieState, QtCore.Qt.CheckStateRole
                )
        self.updateTextAndEmitCheckedItems()

    def updateCheckedItems(self):
        """Function to get the checked items label as list.sans retrouner les categories ,
        il foit y avoir un moyen de le faire avec une aproche plus "model" """
        # il doit y'a
        # print("updateCheckedItems")
        self._checkedItems = []
        self._checkedItemsAndColors = []
        self._itemsStateAndColor = {}
        # self._checkedItemIndexs = []
        self._checkedCategorieItems = collections.OrderedDict()
        categorie = None
        categorieState = QtCore.Qt.Checked
        for index in range(self.count()):
            item = self._model.item(index, 0)
            itemStr = self.itemText(index)
            itemState = item.checkState()
            QColor = self.itemData(index, QtCore.Qt.TextColorRole)
            if QColor is not None:
                itemColor = QColor.getRgb()
            else:
                itemColor = None
            self._itemsStateAndColor[itemStr] = (itemState, itemColor)
            if item.isTristate():
                categorie = itemStr
                categorieState = itemState
            else:
                if itemState and categorieState:
                    self._checkedItems.append(itemStr)
                    self._checkedItemsAndColors.append((itemStr, itemColor))
                    if categorie not in self._checkedCategorieItems:
                        self._checkedCategorieItems[categorie] = [itemStr]
                    else:
                        self._checkedCategorieItems[categorie].append(itemStr)
        self.updateText()

    # synchro et serialisation
    def setSyncModule(self, value):
        self._sync.syncModule = value

    def getSyncModule(self):
        return self._sync.syncModule

    syncModule = QtCore.pyqtProperty(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        self._sync.syncName = value
        # print('setSyncName : ' + value)

    def getSyncName(self):
        return self._sync.syncName

    syncName = QtCore.pyqtProperty(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        self._sync.save = value

    def getSyncSave(self):
        return self._sync.save

    syncSave = QtCore.pyqtProperty(bool, getSyncSave, setSyncSave)

    def setSerialize(self, value):
        self._serialize = value

    def getSerialize(self):
        return self._serialize

    serialize = QtCore.pyqtProperty(bool, getSerialize, setSerialize)


class ItemCategorieStateColor:
    def __init__(
        self, name, categorie=None, state=False, color=None, isCategorie=False
    ):
        self.name = name
        self.categorie = categorie
        self.state = state
        self.color = color
        self.isCategorie = isCategorie  # va servir pour serialisation


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    widget = CheckComboBoxUI()
    widget.addCategorie("Villes")
    widget.addItems(["Paris", "Lille", "Lyon", "Marseille"])
    widget.addCategorie("Prenoms")
    widget.addItems(["Martin", "Baptiste", "Remi", "Helene"])
    widget.addItemWithoutDuplicate(ItemCategorieStateColor("Brest", "Villes", True))
    widget.addItemWithoutDuplicate(ItemCategorieStateColor("Brest", "Villes", True))
    # widget.clear()
    widget.show()
    app.exec_()
