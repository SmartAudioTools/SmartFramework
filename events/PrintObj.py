from qtpy import QtCore, QtWidgets


class PrintObj(QtCore.QObject):
    def __init__(self, parent=None, text=""):
        super(PrintObj, self).__init__(parent)
        self.text = text

    @QtCore.Slot()
    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    @QtCore.Slot(object)
    def input(self, obj=None):
        if self.text:
            print(self.text)
        print("id : " + str(id(obj)))
        print("type : " + str(type(obj)))
        print("value : ", end=" ")
        print(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = PrintObj()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
