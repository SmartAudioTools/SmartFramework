# from qtpy.Qt import *
# ,QwtPlotCurve,QwtPlotItem,QwtLegend:
from qtpy.Qwt5 import QwtPlot, QwtPlotMarker, QwtPlotGrid
from qtpy import QtCore, QtGui
from qtpy.QtCore import Qt
from SmartFace.pyQwtTools import Curve, X1, Y1
from SmartFramework.ui.CheckComboBoxUI import ItemCategorieStateColor


class SmartPlotUI(QwtPlot):

    # outNewName         = QtCore.Signal((str,),(object,))
    # outNewSubName      = QtCore.Signal((str,),(object,))
    outNewCurve = QtCore.Signal(object)
    outClean = QtCore.Signal()  # permet de clean les menus
    # outVisibleNames    = QtCore.Signal(object) # sert pour restaurer menu pour SmartPlotUi serialise
    # outVisibleSubNames = QtCore.Signal(object) # sert pour restaurer menu pour SmartPlotUi serialise

    def __init__(self, parent=None, objectName=""):
        QwtPlot.__init__(self, parent)

        if objectName is not None:
            self.setObjectName(objectName)
        # self.nameSubNames = {}
        # permet d'attendre d'avoir recu toutes les curves avant de faire un update :
        self._updateTimer = QtCore.QTimer()
        self._updateTimer.setSingleShot(True)
        self._updateTimer.setInterval(0)
        self._updateTimer.timeout.connect(self.updateWithAutoScale)
        # look
        self.setCanvasBackground(QtCore.Qt.white)  # QtCore.Qt.black
        self.enableAxis(Y1, False)
        # self.setLineWidth(10)
        # self.setMidLineWidth(7)
        # self.setStyleSheet("QLabel { border: 0px; }");

        # legend = QwtLegend()
        # legend.setItemMode(QwtLegend.ClickableItem)
        # self.insertLegend(legend, QwtPlot.RightLegend)

        # attach a grid
        # grid = QwtPlotGrid()
        # grid.setMajPen(QtGui.QPen(Qt.lightGray))
        # grid.attach(self)

        self.clean()
        # connections
        # self.legendClicked[QwtPlotItem].connect(self.toggleVisibility)
        # finalize

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def setXMax(self, xMax):
        pass
        self.setAxisScale(X1, 0, xMax)

    @QtCore.Slot(int)
    def setXCursor(self, x):
        if self._xCursor is None:
            xCursor = QwtPlotMarker()
            xCursor.setLineStyle(QwtPlotMarker.VLine)
            xCursor.setLinePen(QtGui.QPen(Qt.red, 2))
            xCursor.attach(self)
            self._xCursor = xCursor
        self._xCursor.setXValue(x)
        self.updateLowPriority()

    @QtCore.Slot()
    def clean(self):
        # self._visibleUnderlineTrackingNameSensColor = {}
        # self._trackingStateColor = {}
        # self._highlightNames = []
        # self._highlightSubNames= []
        # self._highlightCategorieName = (None,None)
        # self._highlightCategorieSubName = (None,None)
        self._xCursor = None  # curseur de lecture
        self.curves = []  # pour la serialisation
        # self.visibleNames = dict()
        # self.visibleSubNames = dict()
        self.clear()
        self.outClean.emit()
        self.show()

    @QtCore.Slot(str, object)
    def inPlot(self, widgetName, curve):
        if widgetName == self.objectName():
            self.addCurve(curve)

    @QtCore.Slot(object)
    def addCurve(self, curve, deserialise=False):
        # for item in self.itemList():
        #    if item.title().text() == curve.title().text():
        #        item.

        # if curve.title().text()
        # self.itemList() # me rajoute un  qtpy.Qwt5.Qwt.QwtPlotMarker.__new__(qtpy.Qwt5.Qwt.QwtPlotMarker) a la fin qui fou la merde:
        self.curves.append(curve)
        curve.setVisible(curve.visibleByDefault)
        curve.attach(self)
        self.outNewCurve.emit(curve)
        # name

        """ if deserialise :
            self.outNewName[object].emit(ItemCategorieStateColor(curve.name,curve.categorie ))
            if hasattr(curve,'subName') and (curve.subName is not None):
                self.outNewSubName[object].emit(ItemCategorieStateColor(curve.subName,curve.subCategorie))
        else: 
                       
            self.outNewName[object].emit(ItemCategorieStateColor(curve.name,curve.categorie,curve.visibleByDefault))
            if curve.visibleByDefault :
                if curve.categorie not in self.visibleNames:
                    self.visibleNames[curve.categorie] = [curve.name]
                elif curve.name not in self.visibleNames[curve.categorie]:
                    self.visibleNames[curve.categorie].append(curve.name)
            if hasattr(curve,'subName') and (curve.subName is not None):
                self.outNewSubName[object].emit(ItemCategorieStateColor(curve.subName,curve.subCategorie,curve.visibleByDefault))
                if curve.visibleByDefault :
                    if curve.subCategorie not in self.visibleSubNames:
                        self.visibleSubNames[curve.subCategorie]= [curve.subName]                        
                    elif curve.subName not in self.visibleSubNames[curve.subCategorie]:
                        self.visibleSubNames[curve.subCategorie].append(curve.subName)"""
        self.clearZoomStack()
        self.updateLowPriority()

    def setCurves(self, curves):
        for curve in curves:
            self.addCurve(curve, deserialise=False)
        # self.updateFilterLowPriority()

    @QtCore.Slot()
    def updateLowPriority(self):
        self._updateTimer.stop()
        self._updateTimer.start()

    def updateWithAutoScale(self):
        # print("updateWithAutoScale")
        # self.setAxisAutoScale(QwtPlot.yLeft)
        self.replot()

    # def getState(self):
    #
    #    return self.__dict__

    # pour le zoom

    def mousePressEvent(self, event):
        # print("mousePressEvent")
        self.setFocus()
        if event.button() == QtCore.Qt.LeftButton:
            # self._movingReadHead = True
            # self.setCursor(QtCore.Qt.BlankCursor)
            self.setCursor(QtCore.Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        # self._movingReadHead = False
        self.setCursor(QtCore.Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        if event.buttons():
            if self._movingReadHead:
                pass

    def clearZoomStack(self):
        """Force autoscaling and clear the zoom stack"""
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)
        # self.setAxisAutoScale(QwtPlot.xBottom)
        # self.setAxisAutoScale(QwtPlot.xTop)
        self.replot()
        # for zoomer in self.zoomers:
        #    zoomer.setZoomBase()

    '''def toggleVisibility(self, plotItem):
        """Toggle the visibility of a plot item
        """
        plotItem.setVisible(not plotItem.isVisible())
        self.replot()'''


if __name__ == "__main__":
    import sys
    import numpy
    from SmartFace.pyQwtTools import Pen

    app = QtWidgets.QApplication(sys.argv)
    widget = SmartPlotUI()
    x = numpy.arange(100)
    y = numpy.hanning(100)
    widget.addCurve(
        Curve(
            x, y, name="hanning", pen=Pen(Qt.black), symbol=None, visibleByDefault=True
        )
    )
    y[30:60] = numpy.random.rand(30)
    widget.show()
    app.exec_()