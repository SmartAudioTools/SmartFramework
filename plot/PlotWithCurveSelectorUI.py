# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.plot.PlotUI import PlotUI
from SmartFramework.plot.CurveSelectorUI import CurveSelectorUI


class PlotWithCurveSelectorUI(QtWidgets.QWidget):

    # constructor

    def __init__(self, parent=None, sortingEnabled=True, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)

        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QtWidgets.QSplitter(self)

        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.plotui = PlotUI(self.splitter, *args, **kwargs)
        self.curveselectorui = CurveSelectorUI(self.splitter, sortingEnabled)
        self.horizontalLayout.addWidget(self.splitter)
        self.splitter.setStretchFactor(0, 1)
        # connexions
        self.plotui.outNewCurve[object].connect(self.curveselectorui.addCurve)
        self.plotui.outSelectedCurve[object].connect(self.curveselectorui.selectCurve)

        # geometry
        self.resize(1223, 906)

    # def inPlot[object].connect(self.plotui.addCurve)

    @QtCore.Slot(object)
    def addCurve(self, curve, resetZoom=True):
        self.plotui.addCurve(curve, resetZoom)

    # ajout / supression de curves
    @QtCore.Slot(str, object)
    def inPlot(self, widgetName, curve):
        self.plotui.inPlot(widgetName, curve)

    @QtCore.Slot(int)
    def setXCursor(self, x):
        self.plotui.setXCursor(x)


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = PlotWithCurveSelectorUI()
    widget.setWindowTitle(os.path.splitext(os.path.split(__file__)[1])[0])
    widget.show()
    app.exec_()
