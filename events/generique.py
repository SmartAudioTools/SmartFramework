from qtpy import QtCore, QtGui, QtWidgets


class Generique(QtCore.QObject):

    output = QtCore.Signal((object,), (int,), (float,), (str,))

    def __init__(self, parent=None, expr="+"):
        super(Generique, self).__init__(parent)
        # self.__dict__.update(locals())  # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.expr = expr

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(str)
    def input(self, in1=None):
        if in1 != None:
            self.in1Value = in1
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
                self.val = eval("in1" + self._expr + "in2")
                self.outVal()
            except:
                pass

    def outVal(self):
        obj = self.val
        if type(obj) in (int, float, str):
            self.output[type(obj)].emit(obj)
        self.output[object].emit(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Generique()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())