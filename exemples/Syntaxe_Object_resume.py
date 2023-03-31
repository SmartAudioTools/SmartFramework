# -*- coding: utf-8 -*-

# imports ----

from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.syncObjectUI import SyncObjectUI
from SmartFramework.tools.objects import addArgs, add_Args

## class Monobject(QtCore.QObject):
## class MonobjectUI(QtWidgets.QWidget):
class MonobjectSyncableUI(SyncObjectUI):

    # constructor ------------

    def __init__(self, parent=None, value=0):

        # synchronisation  --------
        SyncObjectUI.__init__(self, parent)
        self.output.connect(self.sync.input)
        self.sync.output[object].connect(self.input)

        # création des attributs  --------

        self.__dict__.update(locals())
        addArgs(locals())
        add_Args(locals())
        self._value = value

        # initialisation
        self.resize(50, 22)

        # création des connexions
        self.monSignal.connect(slot / methode / fonction)
        self.monSignal[float].connect(slot)
        self.monSignal.connect(
            slot, type=qtpy.QtCore.Qt.AutoConnection
        )  # Auto Connection(défaut)/Direct Connection/Queued Connection/Blocking Queued Connection/Unique Connection

        # déconnexion ?
        self.monSignal.disconnect(slot)
        self.monSignal.disconnect()

    # signaux ------------

    outValue = QtCore.Signal(
        float
    )  ## le prefixe "out" permet d'eviter conflit de noms  (avec atribut , methode , propriété ou argument qui sera transformé en propriete)
    monSignal = QtCore.Signal(name="trueSignal")
    monSignal = QtCore.Signal()
    monSignal = QtCore.Signal(bool)  # /int/float/str/object)
    monsignal = QtCore.Signal(int, int)
    monSignal = QtCore.Signal((int,), (float,))

    # slots -----------------

    @QtCore.Slot(float)
    def setValue(
        self, value
    ):  ## si le slot / methode n'emet pas de signal (entrée froide)
        ##self.value =  value                  ## A EVITER CAR POSERA PROBLEME SI TRANSFORME EN PROPRIETE  => BOUCLE INFINIE
        self.__dict__["value"] = value
        self._value = value

    @QtCore.Slot(float)
    def inValue(self, value):  ## si le slot / methode emet un signal (entrée chaude)
        ##self.value =  value                ## A EVITER CAR POSERA PROBLEME SI TRANSFORME EN PROPRIETE  => BOUCLE INFINIE
        self.__dict__["value"] = value
        self._value = value
        self.outValue.emit(value)

    @QtCore.Slot()  ## si on souhaite pouvoir recuperer une valeure avec un "bang"
    def getValue(self):
        self.outValue.emit(self.__dict__["value"])
        self.outValue.emit(self._value)
        return self.__dict__["value"]
        return self._value

    @QtCore.Slot(name="trueSlot")
    @QtCore.Slot()
    @QtCore.Slot(bool)
    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(str)
    @QtCore.Slot(object)
    @QtCore.Slot(int, int)
    @QtCore.Slot(QObject)
    def monSlot(self, obj):
        """C++: int foo(QObject *)"""

    # propriétés                         ## on evitera en général de créer le getter et la propriété ? et se contentera de coder methode setter si dessus .

    def setValue(self, value):
        self.__dict__["value"] = value
        self._value = value

    def getValue(self):
        return self.__dict__["value"]
        return self._value

    value = QtCore.Property(int, getValue, setValue)

    # methodes pour size ------

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(100, 100)

    # serialization -----------

    def __getstate__(self):
        if self.serialize:
            return {"value": self.value}

    def __setstate__(self, state):
        self.__dict__.update(state)

    # methodes  -------

    def outputObject(self, obj):
        self.monSignal.emit()
        self.monSignal.emit(arg1, arg2)
        self.monSignal[float].emit(f)
        self.monSignal[object].emit(obj)

    # Events -----------

    def closeEvent(self, QCloseEvent):
        # QCloseEven.ignore() # si on veut empecher fermeture fenetre:
        QCloseEvent.accept()

    def paintEvent(self, event):
        painter = QtUI.QPainter()
        painter.begin(self)
        painter.end()

    def mousePressEvent(self, event):
        print("mouse pressed !!!")
        if event.button() == QtCore.Qt.RightButton:
            pass
        else:
            pass
        # informe Qt  que l'evenement à été traité .sinon il est propagé au widgets parents de l’objet cible initial. jusqu’à être géré ou que l’objet QApplication soit atteint.:
        event.accept()

    def mouseReleaseEvent(self, event):
        event.accept()

    def mouseMoveEvent(self, event):
        X = QtGui.QCursor.pos().x()
        Y = QtGui.QCursor.pos().y()
        event.accept()

    def keyPressEvent(self, event):
        print("key pressed !!!!")
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        event.accept()

    def keyReleaseEvent(self, event):
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = MonobjetUI()
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()