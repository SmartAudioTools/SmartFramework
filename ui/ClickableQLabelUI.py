# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.Sync import Sync


class ClickableQLabelUI(QtWidgets.QLabel):

    clicked = QtCore.Signal()
    doubleClicked = QtCore.Signal()

    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

    # souris
    def mousePressEvent(self, event):
        self.clicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ClickableQLabelUI()
    widget.show()
    app.exec_()
