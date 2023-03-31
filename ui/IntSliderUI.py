# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets


class IntSliderUI(QtWidgets.QSlider):
    def __init__(self, parent=None, **kwargs):
        QtWidgets.QSlider.__init__(self, parent, **kwargs)
        self.setOrientation(QtCore.Qt.Horizontal)

    @QtCore.Slot(int)
    def setMaximum(self, max):
        QtWidgets.QSlider.setMaximum(self, max)

    @QtCore.Slot(int)
    def setMinimum(self, max):
        QtWidgets.QSlider.setMaximum(self, max)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = IntSliderUI()
    widget.show()
    app.exec_()
