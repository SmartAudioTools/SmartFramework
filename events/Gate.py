# -*- coding: utf-8 -*-
from qtpy import QtCore, QtWidgets


class Gate(QtCore.QObject):
    # Constructor

    def __init__(self, parent=None):
        super(Gate, self).__init__(parent)
        self._gate = False

    # signals

    output = QtCore.Signal((object,), (bool,), (int,), (float,), (str,))

    # slots

    @QtCore.Slot(object)
    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    def input(self, obj):
        if self._gate:
            self.output[object].emit(obj)
            if type(obj) in [bool, int, float, str]:
                self.output[type(obj)].emit(obj)

    # properties

    @QtCore.Slot(bool)
    def setGate(self, b):
        self._gate = b

    def getGate(self):
        return self._gate

    gate = QtCore.Property(float, getGate, setGate)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Gate()
    app.exec_()
