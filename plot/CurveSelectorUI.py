# import os
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt

# from pyQwtTools import Curve
from SmartFramework.tools.dictionaries import reverseDict

# from SmartFramework.ui.FlonumUI import FlonumUI
# from qtpy.Qwt5 import QwtPlotCurve
eventNames = reverseDict(QtCore.QEvent.__dict__)


class CurveSelectorUI(QtWidgets.QTreeWidget):
    outSelectedCurve = QtCore.Signal(object)
    outDoubleClick = QtCore.Signal()

    def __init__(self, parent=None, sortingEnabled=True):
        QtWidgets.QTreeWidget.__init__(self, parent)
        # self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setSortingEnabled(sortingEnabled)
        self.setColumnWidth(1, 30)
        self.header().close()
        self._trackingStateColor = {}
        # self.i=0       # compteur pour affichage des evenement lors de debugage
        self.viewport().installEventFilter(self)
        self._lastItem = None  # evite d'envoyer plein de messages quand survol souris
        # self.installEventFilter(self)
        # This signal is emitted when the contents of the column in the specified item changes.:
        self.itemChanged.connect(self.itemChangedEvent)
        # This signal is emitted when the current item changes. The current item is specified by current, and this replaces the previous current item.:
        self.currentItemChanged.connect(self.updateSelected)

    def child(self, itemIndex):
        return self.topLevelItem(itemIndex)

    def childCount(self):
        return self.topLevelItemCount()

    def addItem(self, names, parent, visible):
        for childIndex in range(parent.childCount()):
            item = parent.child(childIndex)
            if item is None:
                print("bug")
            elif item.text(0) == names[0]:
                break
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setText(0, names[0])

        if visible is True:
            item.setCheckState(0, QtCore.Qt.Checked)
        elif (len(names) == 1) or (not item.checkState(0)):
            # permet de forcer la création d'une checkbox:
            item.setCheckState(0, QtCore.Qt.Unchecked)
        if len(names) > 1:
            if names[0] == visible:
                visible = True
            return self.addItem(names[1:], item, visible)
        else:
            return item

    @QtCore.Slot(object)
    def addCurve(self, curve, deserialise=False):
        if isinstance(curve.name, str):
            names = [curve.name]
        else:
            names = curve.name
        parent = self
        item = self.addItem(names, parent, curve.visibleByDefault)

        if hasattr(item, "curves"):
            item.curves.append(curve)  # [curve.trackingName] = curve
        else:
            # {curve.trackingName : curve} # utilis un dictionnaire au lieu d'une liste pourquoi déjà ? pour evtier de rajouter plusieus fois meme courbe ? :
            item.curves = [curve]
        if curve.trackingName in self._trackingStateColor:
            trackingStateColor = self._trackingStateColor[curve.trackingName]
            curve.setColor(trackingStateColor["color"])
            curve.setUnderline(trackingStateColor["underline"])
            curve.setVisible(self.isVisible(item) & trackingStateColor["visible"])
            if trackingStateColor["direction"] < 0:
                curve.setStyle(Qt.DotLine)
        else:
            curve.setVisible(self.isVisible(item))
            if hasattr(curve, "pen"):
                color = QtGui.QColor(curve.pen.color())
            elif curve.color is not None:
                color = QtGui.QColor(*curve.color)
            color.setAlpha(255)
            item.setForeground(0, color)

        # scaleWidget = FlonumUI(self)
        # self.setItemWidget(item,1,scaleWidget)
        for plot in curve.plots():
            plot.update()

    @QtCore.Slot(object)
    def selectCurve(self, curve):
        if curve is None:
            self.clearSelection()
            unselectedCurves = self._lastItem.curves
            for unselectedCurve in unselectedCurves:  # .values():
                unselectedCurve.setSelected(False)
            # self._lastItem = None
            self.setCurrentItem(None)
        else:
            for item in self.itemsIterator(self):
                if hasattr(item, "curves") and curve in item.curves:  # .values():
                    self.setCurrentItem(item)
                    return

    def itemsIterator(self, item):
        yield item
        for childIndex in range(item.childCount()):
            for childItem in self.itemsIterator(item.child(childIndex)):
                yield childItem

    def updateSelected(self, item):

        # print("currentItemChanged",item)
        # print("currentItemChanged")
        if self._lastItem is not item:  # and item == self.currentItem():
            if hasattr(item, "curves"):
                newSelectedCurves = item.curves
                for newSelectedCurve in newSelectedCurves:  # .values():
                    newSelectedCurve.setSelected(True)
                    self.outSelectedCurve.emit(newSelectedCurve)
                    for plot in newSelectedCurve.plots():
                        plot.update()
            if hasattr(self._lastItem, "curves"):
                lastSelectedCurves = self._lastItem.curves
                for lastSelectedCurve in lastSelectedCurves:  # .values():
                    lastSelectedCurve.setSelected(False)
                    for plot in lastSelectedCurve.plots():
                        plot.update()
            self._lastItem = item

    def itemChangedEvent(self, item, column):
        if column == 0:
            visibleItem = self.isVisible(item)
            self.recursiveUpdateVisibility(item, visibleItem)

    def isVisible(self, item):
        if not item.checkState(0):
            return False
        else:
            parent = item.parent()
            if parent is not None:
                return self.isVisible(item.parent())
            else:
                return True

    @QtCore.Slot(object)
    def inTrackingStateColor(self, trackingStateColor):
        self._trackingStateColor = trackingStateColor
        self.recursiveUpdateVisibility(self, True)
        # self.updateFilterLowPriority()

    def recursiveUpdateVisibility(self, item, visibleItem):
        if hasattr(item, "curves"):
            curves = item.curves
            for curve in curves:
                trackingName = curve.trackingName
                if trackingName in self._trackingStateColor:
                    trackingStateColor = self._trackingStateColor[trackingName]
                    if trackingStateColor["direction"] < 0:
                        curve.setStyle(Qt.DotLine)
                    curve.setColor(trackingStateColor["color"])
                    curve.setUnderline(trackingStateColor["underline"])
                    curve.setVisible(visibleItem & trackingStateColor["visible"])
                else:
                    curve.setVisible(visibleItem)
        # else :
        for childItem in [
            item.child(childIndex) for childIndex in range(item.childCount())
        ]:
            if childItem.checkState(0):
                self.recursiveUpdateVisibility(childItem, visibleItem)
            else:
                self.recursiveUpdateVisibility(childItem, False)

    def keyPressEvent(self, event):
        # print(event.key())  # print(event.key())
        if event.key() == QtCore.Qt.Key_Backspace:
            currentItem = self.currentItem()
            if currentItem:
                self.removeItem(currentItem)
        else:
            QtWidgets.QTreeWidget.keyPressEvent(self, event)

    @QtCore.Slot(object)
    def removeTrackings(self, trackingNames, item=None):
        if item is None:
            item = self
        for childIndex in reversed(range(item.childCount())):
            childITem = item.child(childIndex)
            self.removeTrackings(trackingNames, childITem)
        if hasattr(item, "curves"):
            for curve in reversed(item.curves):  # .values():
                if curve.trackingName in trackingNames:
                    for plot in curve._plots:
                        plot.removeCurve(curve)
                    item.curves.remove(curve)
            if not item.curves:
                del item.curves
        if not hasattr(item, "curves") and not item.childCount() and item != self:
            parent = item.parent()
            if parent is None:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            else:
                parent.takeChild(parent.indexOfChild(item))

    def removeItem(self, item):
        self._removeItemCurvesAndChildren(item)
        self._removeItemFromParent(item)
        # remove item

    def _removeItemFromParent(self, item):
        parent = item.parent()
        if parent is None:
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        else:
            parent.takeChild(parent.indexOfChild(item))
            if not hasattr(parent, "curves") and not parent.childCount():
                self._removeItemFromParent(parent)

    def _removeItemCurves(self, item):
        if hasattr(item, "curves"):
            for curve in item.curves:
                for plot in curve._plots:
                    plot.removeCurve(curve)

    def _removeItemCurvesAndChildren(self, item):
        self._removeItemCurves(item)
        for childIndex in reversed(range(item.childCount())):
            self._removeItemCurvesAndChildren(item.child(childIndex))
        item.takeChildren()

    def eventFilter(self, obj, event):
        """Function to filter out the unwanted events and add new functionalities for it."""
        eventType = event.type()
        # self.i+=1
        if obj == self.viewport():
            # print(eventNames[eventType])
            if eventType in [
                QtCore.QEvent.MouseButtonPress,
                QtCore.QEvent.MouseButtonDblClick,
            ]:
                # permet de gerer deuxième clic d'un double-clic comme un simple clic et d'etre ainsi plus réactif pour décocher une courbe

                if eventType == QtCore.QEvent.MouseButtonDblClick:
                    self.outDoubleClick.emit()

                if event.button() == QtCore.Qt.RightButton:
                    # ne fait pas de difference entre les column... toujours le meme :
                    item = self.itemAt(event.pos())
                    if item.childCount():
                        if item.checkState(0):
                            item.setCheckState(0, QtCore.Qt.Unchecked)
                            for childItem in [
                                item.child(childIndex)
                                for childIndex in range(item.childCount())
                            ]:
                                childItem.setCheckState(0, QtCore.Qt.Unchecked)
                        else:
                            item.setCheckState(0, QtCore.Qt.Checked)
                            for childItem in [
                                item.child(childIndex)
                                for childIndex in range(item.childCount())
                            ]:
                                childItem.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        # bloque en attendant couleure ?:
                        color = QtWidgets.QColorDialog.getColor(
                            item.foreground(0).color(),
                            self,
                            "chose Color",
                            QtWidgets.QColorDialog.ColorDialogOptions(1),
                        )
                        if color.isValid():
                            item.setForeground(0, color)
                            for curve in item.curves:
                                curve.setColor(color)
                    return True

                if event.button() == QtCore.Qt.LeftButton:
                    item = self.itemAt(event.pos())
                    if item is not None:
                        selected = item.isSelected()
                    else:
                        selected = False
                    QtWidgets.QTreeView.mousePressEvent(self, event)
                    if selected:
                        self.setCurrentItem(None)
                    return True
        return False


if __name__ == "__main__":
    import sys
    import numpy
    from SmartFramework.plot.PlotUI import Curve, Pen

    app = QtWidgets.QApplication(sys.argv)
    widget = CurveSelectorUI()
    x = numpy.arange(100)
    y = numpy.hanning(100)
    widget.addCurve(
        Curve(
            x,
            y,
            name=["Tracking2D", "inconsistance <->", "bouche"],
            pen=Pen([255, 0, 0]),
            visibleByDefault=True,
        )
    )
    y[30:60] = numpy.random.rand(30)
    widget.show()
    app.exec_()
