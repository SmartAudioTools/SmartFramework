from qtpy import QtCore, QtGui, QtWidgets


class Plus(QtCore.QObject):

    output = QtCore.Signal((object,), (int,), (float,), (str,))

    def __init__(self, parent=None):
        super(Plus, self).__init__( parent)

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(str)
    def input_1(self, val=None):
        if val != None:
            self.In1Value = val
        if hasattr(self, "In2Value"):
            self.val = val + self.In2Value
        else:
            self.val = val
        self.outVal()

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(str)
    def input_2(self, val):
        self.In2Value = val
        if hasattr(self, "In1Value"):
            self.val = val + self.In1Value
        else:
            self.val = val
        self.outVal()

    def outVal(self):
        obj = self.val
        typeObj = type(obj)
        if typeObj in (int, float, str):
            self.output[typeObj].emit(obj)
        self.output[object].emit(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Plus()