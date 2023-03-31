# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets


class EditableRadioButtonUI(QtWidgets.QRadioButton):
    # sort pour selection d'un nom , mais ni pour creation ou renomage ? ( a verifier) trop compliqué d'empecher la sortie de stringOut pour une creation ? pas souhaité? :
    stringOut = QtCore.Signal(str)
    stringRename = QtCore.Signal(str, str)
    stringCreate = QtCore.Signal(str)

    def __init__(self, parent=None, forceToName=True):
        QtWidgets.QRadioButton.__init__(self, parent)
        self.forceToName = forceToName

        self.pressed.connect(self.emitText)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.lineEdit.editingFinished.connect(self.editingFinished)
        self.lineEdit.setFrame(False)

        # flag pour empecher de declancher deux fois : 1) quand touche enter : normale 2) quand clic sur autre bouton : perd le focus:
        self.editing = False
        # flag permetant de distinguer si on est en train de créer ou de modifier le text:
        self.creatingNew = False

    def __getstate__(self):
        return {"text": self.text}

    @QtCore.Slot(str)
    def setText(self, text):
        QtWidgets.QRadioButton.setText(self, text.replace("&", "&&"))
        self.lineEdit.setText(text)

    def getText(self):
        return QtWidgets.QRadioButton.text(self).replace("&&", "&")

    text = QtCore.Property(int, getText, setText)

    def emitText(self):
        self.stringOut.emit(self.text)

    def editingFinished(self):
        # print("editingFinished")
        if self.editing:
            # obligé sinon declanche deux fois : 1) quand touche enter : normale 2) quand clic sur autre bouton : perd le focus
            self.editing = False

            self.setText(self.lineEdit.text())
            self.lineEdit.setGeometry(QtCore.QRect(0, 0, 0, 0))
            if self.text != "":
                if self.creatingNew:
                    self.creatingNew = False
                    self.blockSignals(True)
                    self.click()
                    self.blockSignals(False)
                    self.stringCreate.emit(self.text)
                else:
                    self.stringRename.emit(self.text, self.oldText)

    def mousePressEvent(self, event):
        # print('moussePress'  + self.text())
        if self.forceToName and self.text == "":
            print("le text n'existe pas encore je l'edite")
            self.creatingNew = True
            self.editLine()
        else:
            # print('le text existe je peux le cliquer')
            self.click()

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        self.editLine()

    def editLine(self):
        self.editing = True
        self.oldText = self.text
        retinaF = 2
        self.lineEdit.setGeometry(
            QtCore.QRect(15 * retinaF, -3 * retinaF, 300 * retinaF, 20 * retinaF)
        )
        self.lineEdit.setFocus(1)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = EditableRadioButtonUI()
    widget.show()
    sys.exit(app.exec_())
