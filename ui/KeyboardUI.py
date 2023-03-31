# import keyboard
import sys
from qtpy import QtCore, QtWidgets, QtGui, scaled
from SmartFramework.ui.ControlUI import ControlUI


# liste de classes qui ouvrente automatiquement un clavier quand elle recupère le focus :
keyboardAutoShowClasses = (QtWidgets.QLineEdit,)


class KeyboardFake:
    def show(self):
        pass

    def hide(self):
        pass


# permet d'appeller de n'import quel script keboardUI.keyboard.show() et keboardUI.keyboard.hide() , meme si on a pas instencié de KeboardUI:
keyboard = KeyboardFake()


class KeyboardUI(QtWidgets.QWidget):

    keyPressed = QtCore.Signal(str)

    def __init__(self, parent=None, autoShow=True):

        QtWidgets.QWidget.__init__(self, parent)
        self._autoShow = autoShow
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # |QtCore.Qt.Tool : permet d'enlever bouton reduction/agrandissemetn à la fenetre mais empeche affichage quand dans un DockWidget:
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        # ne suffit pas a empecher de prendre le focus quand dans fenetre flotante :
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        layout = QtWidgets.QGridLayout(spacing=0)  # spacing=scaled(1)
        layout.setContentsMargins(0, 0, 0, 0)
        self._keysUp = ["0123456789", "AZERTYUIOP", "QSDFGHJKLM", "▲WXCVBN␣◄✔"]  # 👌 ⏎↵
        self._keysLow = ["()[]!'-+#%", "azertyuiop", "qsdfghjklm", "▲wxcvbn␣◄✔"]
        self._keyTranslate = {
            "▲": QtCore.Qt.Key_Shift,
            "␣": QtCore.Qt.Key_Space,
            "◄": QtCore.Qt.Key_Backspace,
            "✔": QtCore.Qt.Key_Enter,
        }
        for i, line in enumerate(self._keysUp):
            for j, key in enumerate(line):
                isShift = self._keyTranslate.get(key, None) == QtCore.Qt.Key_Shift
                button = ControlUI(
                    text=key,
                    alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
                    checkable=isShift,
                    checked=isShift,
                )
                button.valueChanged[str].connect(self._keyPressed)
                # evite de prendre le focus quand dans MainWindow mais ne suffit pas a empecher de prendre le focus quand dans fenetre flotante :
                button.setFocusPolicy(QtCore.Qt.NoFocus)
                if isShift:
                    button.valueChanged[bool].connect(self.shift)
                layout.addWidget(button, i, j)
        self.setLayout(layout)
        self._recipient = None
        QtWidgets.QApplication.instance().focusChanged.connect(self.focuseChanged)
        # self.findkeyboard()
        # permet d'attendre que les objet soient crée pour chercher le dockWIdget qui contient le keyboard:
        QtCore.QTimer.singleShot(0, self.findkeyboard)

    def focuseChanged(self, old, now):
        if isinstance(now, keyboardAutoShowClasses):
            # permetra de retrouver le QlineEdit, meme si le keyboardUI s'ouvre dans une autre fenetre qui prend le focus et empeche donc de retrouver le QLineEdit via QtWidgets.QApplication.instance().focusWidget() :
            self.recipient = now
            # le seul moyen pour cacher clavier virtuel si appuye sur Enter (le focus reste sur QlineEdit et donc focuseChanged ne permet pas de le detecter ):
            self.recipient.editingFinished.connect(self.editFinished)
            if self._autoShow:
                keyboard.show()

    def editFinished(self):
        self.recipient.editingFinished.disconnect(self.editFinished)
        # if QtWidgets.QApplication.instance().focusWidget() is not None :  # tentative de hack pour emepecher de cacher le clavier quand il tente de s'ouvrire dans un fenetre popup et donc fait perdre au QlineEdit le focus
        # permet d'arreter de faire clignoter le curseur d'edition:
        self.recipient.clearFocus()
        self.recipient = None
        if self._autoShow:
            keyboard.hide()

    def findkeyboard(self):
        global keyboard
        keyboard = self
        parent = self.parent()
        if parent is not None:
            grandParent = parent.parent()
            if isinstance(grandParent, QtWidgets.QDockWidget):
                keyboard = grandParent
        if self._autoShow:
            keyboard.hide()

    def activateWindow(self):
        print("activateWindow()")

    def _keyPressed(self, strKey):
        # print(strKey)
        # keyboard.press_and_release(strKey)
        if strKey in self._keyTranslate:
            intKey = self._keyTranslate[strKey]
            if intKey == QtCore.Qt.Key_Space:
                strKey = " "
            else:
                strKey = None
        else:
            intKey = QtGui.QKeySequence.fromString(strKey)[0]
        if intKey != QtCore.Qt.Key_Shift:
            # permet d'envoyer donnée clavier à une objet qui n'est pas dans keyboardAutoShowClasses:
            recipient = QtWidgets.QApplication.instance().focusWidget()
            if recipient is None:
                # hack qui permet de tout de meme envoyé à un objet si on a perdu le focus a cause de l'ouvertur d'une fenetre :
                recipient = self.recipient
            if recipient is not None:
                event = QtGui.QKeyEvent(
                    QtCore.QEvent.KeyPress, intKey, QtCore.Qt.NoModifier, strKey
                )
                QtWidgets.QApplication.instance().postEvent(recipient, event)
                # QtWidgets.QApplication.instance().processEvents()
                # recipient.event(event)
                event = QtGui.QKeyEvent(
                    QtCore.QEvent.KeyRelease, intKey, QtCore.Qt.NoModifier
                )
                recipient.event(event)
                QtWidgets.QApplication.instance().postEvent(recipient, event)
            # QtWidgets.QApplication.instance().processEvents()
        # if intKey == QtCore.Qt.Key_Enter:
        #    keyboard.hide()

    def shift(self, b):
        if b:
            keys = self._keysUp
        else:
            keys = self._keysLow
        for i, line in enumerate(keys):
            for j, key in enumerate(line):
                button = self.layout().itemAtPosition(i, j).widget()
                button.setText(key)
                button.update()

    def setAutoShow(self, value):
        self._autoShow = value

    def getAutoShow(self):
        return self._autoShow

    autoShow = QtCore.Property(bool, getAutoShow, setAutoShow)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = QtWidgets.QWidget()
    keyboardUI = KeyboardUI()
    layout = QtWidgets.QVBoxLayout(widget)
    layout.addWidget(QtWidgets.QLineEdit())
    layout.addWidget(keyboardUI)
    widget.setFocus()
    widget.show()
    sys.exit(app.exec_())
