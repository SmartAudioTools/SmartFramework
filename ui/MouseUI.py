from qtpy import QtCore, QtWidgets, QtGui

debug = False


class MouseUI(QtWidgets.QWidget):
    mouseX = QtCore.Signal(int)
    mouseY = QtCore.Signal(int)
    mouseRightToggle = QtCore.Signal(bool)
    mouseLeftToggle = QtCore.Signal(bool)
    mouseRightPress = QtCore.Signal()
    mouseRightRelease = QtCore.Signal()
    mouseLeftPress = QtCore.Signal()
    mouseLeftRelease = QtCore.Signal()
    keyPressSig = QtCore.Signal()

    def __init__(self, parent=None, prop1="prop1"):
        QtWidgets.QWidget.__init__(self, parent)
        # permet de recuperer le focus clavier et donc de gerer les keyPressEvent quand on clic sur le widget avec la souris:
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.setMouseTracking(True)                # permet d'activer la capture de mouseMoveEvent (quand passe au dessus du widget), meme sans avoir clique sur bouton souris
        # self.grabMouse()                           # permet d'entendre  la capture sans clic au de la taille du widget (va deja au dela avec clic) (ATTENTION on desactive tout les autres widgets...)
        self.x = 0
        self.y = 0

    def setProp1(self, value):
        self.__dict__["prop1"] = value

    def getProp1(self):
        return self.__dict__["prop1"]

    prop1 = QtCore.Property(str, getProp1, setProp1)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.end()

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(100, 100)

    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.RightButton:
            self.mouseRightPress.emit()
            self.mouseRightToggle.emit(True)
            if debut:
                print("mouse press right")
        else:
            self.mouseLeftPress.emit()
            self.mouseLeftToggle.emit(True)
            if debut:
                print("mouse press left")
        self.oldX = QtGui.QCursor.pos().x()
        self.oldY = QtGui.QCursor.pos().y()
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        event.accept()

    def mouseMoveEvent(self, event):
        newX = QtGui.QCursor.pos().x()
        newY = QtGui.QCursor.pos().y()
        deltaX = newX - self.oldX
        deltaY = newY - self.oldY
        self.x = self.x + deltaX
        self.y = self.y + deltaY

        QtGui.QCursor.setPos(self.oldX, self.oldY)
        self.mouseX.emit(self.x)
        self.mouseY.emit(self.y)

        # self.mouseX.emit(QtUI.QCursor.pos().x())
        # self.mouseY.emit(QtUI.QCursor.pos().y())
        # self.mouseX.emit(event.globalX())
        # self.mouseY.emit(event.globalY())
        # self.mouseX.emit(event.x())
        # self.mouseY.emit(event.y())
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.mouseRightRelease.emit()
            self.mouseRightToggle.emit(False)
        else:
            self.mouseLeftRelease.emit()
            self.mouseLeftToggle.emit(False)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        event.accept()

    def keyPressEvent(self, event):
        print("key pressed !!!!")
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        self.keyPressSig.emit()
        event.accept()


if __name__ == "__main__":
    import sys

    debug = True
    app = QtWidgets.QApplication(sys.argv)
    widget = MouseUI()
    widget.show()
    sys.exit(app.exec_())
