from qtpy import QtCore, QtWidgets


class LineEditUI(QtWidgets.QLineEdit):
    textEntered = QtCore.Signal(str)

    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.returnPressed.connect(self.emitTextEntered)

    def emitTextEntered(self):
        self.textEntered.emit(self.text())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = LineEditUI()
    widget.show()
    app.exec_()
