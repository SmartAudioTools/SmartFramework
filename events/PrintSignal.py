from qtpy import QtCore, QtGui, QtWidgets


class PrintSignal(QtCore.QObject):
    def __init__(self, parent=None, text=""):
        super(PrintSignal, self).__init__( parent)

    @QtCore.Slot()
    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    @QtCore.Slot(object)
    def input(self, obj=None):
        sender = self.sender()
        metaMethod = sender.metaObject().method(self.senderSignalIndex())
        # metaMethod.name()
        # metaMethod.methodSignature()
        print(
            f'{sender.objectName()}.{bytes(metaMethod.methodSignature()).decode("utf_8")} : {obj}'
        )
        # if self.text:
        #    print(self.text)
        # print("id : " + str(id(obj)))
        # print("type : " + str(type(obj)))
        # print("value : ", end=" ")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = PrintObj()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
