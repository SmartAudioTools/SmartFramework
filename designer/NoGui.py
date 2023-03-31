from qtpy import QtCore, QtGui


class NoGui(QtCore.QObject):
    outImage = QtCore.Signal(object)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        print("__init__")
        # reaz = oiu

    # def sizeHint(self):
    #   return QtCore.QSize(100,100)
    @QtCore.Slot()
    def start(self):
        pass


NoGui = type("NoGui", (QtWidgets.QWidget,), dict(NoGui.__dict__))
# print(NoGui.__dict__)
# print(NoGui.__bases__)
# NoGui.__bases__= (QtWidgets.QWidget,)
# print(NoGui.__bases__)
# print(NoGui.__dict__)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = NoGui()
    widget.show()
    app.exec_()
