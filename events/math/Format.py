from qtpy import QtCore, QtWidgets


class Eval2(QtCore.QObject):

    output = QtCore.Signal((object,), (int,), (float,), (str,))

    def __init__(self, parent=None, expr="+"):
        super(Eval2, self).__init__( parent)
        self._expr = expr

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(str)
    def in1(self, in1=None):
        self.evalValue()

    @QtCore.Slot(object)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(str)
    def input_2(self, in2):
        self.in2Value = in2
        self.evalValue()

    def evalValue(self):
        try:
            in1 = self.in1Value
            in2 = self.in2Value
        except:
            pass
        try:
            self.val = eval(self._expr)
            self.outVal()
        except:
            try:
                self.val = eval("in1" + self._expr)
                self.outVal()
            except:
                print("impossible d'evaluer")

    def outVal(self):
        obj = self.val
        typeObj = type(obj)
        if typeObj is int:
            self.output[int].emit(obj)
        elif typeObj is float:
            self.output[float].emit(obj)
        elif typeObj is str:
            self.output[str].emit(obj)
        self.output[object].emit(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Eval2()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())