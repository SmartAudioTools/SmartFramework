from qtpy import QtCore, QtGui, QtWidgets


class ToPython(QtCore.QObject):
    output = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(ToPython, self).__init__(parent)

    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    @QtCore.Slot(object)
    def input(self, obj=None):
        self.output.emit(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ToPython()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
