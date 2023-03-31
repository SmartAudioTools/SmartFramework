from qtpy import QtCore, QtGui, QtWidgets


class Properties(QtCore.QObject):
    def __init__(self, parent=None, prop1="prop1", prop2="prop2", prop3=3, prop4=4.0):
        super(Properties, self).__init__(parent)
        self.__dict__.update(locals())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Properties()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
