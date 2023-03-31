# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.plot.PlotUI import PlotUI
from SmartFramework.plot.CurveSelectorUI import CurveSelectorUI


class PlotWithCurveSelectorUnblockingUI(QtWidgets.QDialog):

    # constructor

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(self)

        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.plotui = PlotUI(self.splitter)
        self.curveselectorui = CurveSelectorUI(self.splitter)
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


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    plotUI = PlotWithCurveSelectorUnblockingUI()
    plotUI.show()
    app.processEvents()
    # self.exec_()

    # widget.show()
    # widget.exec()
    # app.exec_()
