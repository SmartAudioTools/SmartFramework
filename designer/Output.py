from qtpy import QtCore, QtGui, QtWidgets


class Output(QtCore.QObject):
    def __init__(self, parent=None):
        super(Output, self).__init__(parent)

    @QtCore.Slot(object)
    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    def input(self, val):
        pass
