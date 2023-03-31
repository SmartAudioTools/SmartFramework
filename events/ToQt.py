from qtpy import QtCore, QtGui, QtWidgets


class ToQt(QtCore.QObject):
    # objet en premier pour etre par defaut
    output = QtCore.Signal((object,), (bool,), (int,), (float,), (str,))

    def __init__(self, parent=None):
        super(ToQt, self).__init__(parent)

    @QtCore.Slot(object)
    def input(self, obj=None):
        if type(obj) in [bool, int, float, str]:
            self.output[type(obj)].emit(obj)
        else:
            self.output[object].emit(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ToQt()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
