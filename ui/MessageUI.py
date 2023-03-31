# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets


class MessageUI(QtWidgets.QPushButton):

    stringOut = QtCore.Signal(str)
    objectOut = QtCore.Signal((object,), (bool,), (int,), (float,), (str,))

    def __init__(self, parent=None, text="", **kwargs):
        super(MessageUI, self).__init__(parent, **kwargs)
        self.pressed.connect(self.bang)
        self.toggled.connect(self.bang)
        self.text = text

    def stringOutSend(self):
        if self.text:
            self.stringOut.emit(self.text)

    def objectOutSend(self):
        try:
            val = eval(self.text)
            typeVal = type(val)
            if typeVal in (bool, int, float, str):
                self.objectOut[typeVal].emit(val)
            self.objectOut[object].emit(val)
        except:
            pass

    # slots
    @QtCore.Slot()
    def bang(self, send=True):
        if send:
            self.stringOutSend()
            self.objectOutSend()

    # properties
    text = QtCore.Property(
        str, QtWidgets.QPushButton.text, QtWidgets.QPushButton.setText
    )


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MessageUI()
    widget.show()
    sys.exit(app.exec_())