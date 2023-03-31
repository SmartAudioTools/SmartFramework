from qtpy import QtCore, QtGui, QtWidgets


class ColorUI(QtWidgets.QWidget):
    outColor = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None, color=QtGui.QColor(0, 255, 0, 255), **kwargs):
        # synchronisation
        QtWidgets.QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.color = color

    def mousePressEvent(self, event):
        # bloque en attendant couleure ?:
        self.color = QtWidgets.QColorDialog.getColor(
            self.color,
            self,
            "chose Color",
            QtWidgets.QColorDialog.ColorDialogOptions(1),
        )

    @QtCore.Slot(object)
    @QtCore.Slot(QtGui.QColor)
    def setColor(self, color):
        self.__dict__["color"] = color
        p = self.palette()
        p.setColor(QtGui.QPalette.Window, color)
        self.setPalette(p)

        self.outColor.emit(color)
        self.update()

    def getColor(self):
        return self.__dict__["color"]

    color = QtCore.Property(QtGui.QColor, getColor, setColor)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ColorUI()
    widget.show()
    app.exec_()
