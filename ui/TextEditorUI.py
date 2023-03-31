from qtpy import QtCore, QtWidgets


class TextEditorUI(QtWidgets.QPlainTextEdit):

    textChangedStr = QtCore.Signal(str)

    def __init__(self, parent=None):
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.textChanged.connect(self.emitText)
        QtCore.QTimer.singleShot(0, self.emitText)

    def emitText(self):
        self.textChangedStr.emit(self.document().toPlainText())

    def __getstate__(self):
        return {"plainText": self.document().toPlainText()}


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = TextEditorUI()
    widget.show()
    app.exec_()
