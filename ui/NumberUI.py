# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.Sync import Sync


class NumberUI(QtWidgets.QSpinBox):
    def __init__(
        self,
        parent=None,
        value=0,
        mouseSensibility=0.1,
        minimum=0,
        maximum=99,
        repeat=False,
        syncModule="synced",
        syncName="",
        syncSave=True,
        serialize=True,
        sendInitValue=True,
        sendSetValue=True,
        **kwargs
    ):
        QtWidgets.QSpinBox.__init__(self, parent, **kwargs)
        # synchronisation & serialization
        self._sync = Sync(self, syncModule=syncModule, syncName=syncName, save=syncSave)
        self.valueChanged.connect(self._sync.input)
        self._sync.output[int].connect(self.setValue)
        self._serialize = serialize

        # properties
        self._initValue = value
        self.mouseSensibility = mouseSensibility
        self._repeat = repeat
        self.setMaximum(maximum)
        self.setMinimum(minimum)
        self._sendInitValue = sendInitValue
        self._sendSetValue = sendSetValue

        # intern
        # Flag qui permet de savoir si on utilise un touch screen en attendant QT5 qui devrait permet de ne plus confondre un mouvement de souris et de touch:
        self._useTouchScreen = False
        self._lineEdit = self.lineEdit()
        self._lineEdit.installEventFilter(self)
        # permet de detecter un touch event :
        self._lineEdit.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)
        self._initialized = False
        self._oldX = 0
        self._oldY = None
        QtCore.QTimer.singleShot(0, self.setInitValue)

    #  SpinBox properties -> slots

    @QtCore.Slot(int)
    def setMaximum(self, max):
        QtWidgets.QSpinBox.setMaximum(self, max)

    # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)         :
    maximum = QtCore.Property(
        int, QtWidgets.QSpinBox.maximum, QtWidgets.QSpinBox.setMaximum
    )

    @QtCore.Slot(int)
    def setMinimum(self, max):
        QtWidgets.QSpinBox.setMinimum(self, max)

    # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)        :
    minimum = QtCore.Property(
        int, QtWidgets.QSpinBox.minimum, QtWidgets.QSpinBox.setMinimum
    )

    @QtCore.Slot(str)
    def setPrefix(self, string):
        QtWidgets.QSpinBox.setPrefix(self, string)

    @QtCore.Slot(str)
    def setSuffix(self, string):
        QtWidgets.QSpinBox.setSuffix(self, string)

    @QtCore.Slot(int)
    def setDecimals(self, value):
        QtWidgets.QDoubleSpinBox.setDecimals(self, value)

    # slots

    @QtCore.Slot(str)
    def setUnity(self, string):
        QtWidgets.QSpinBox.setSuffix(self, " " + string)

    @QtCore.Slot(bool)
    def setLog(self, log):
        self._log = log

    # properties

    def setSendInitValue(self, value):
        self._sendInitValue = value

    def getSendInitValue(self):
        return self._sendInitValue

    sendInitValue = QtCore.Property(bool, getSendInitValue, setSendInitValue)

    def setSendSetValue(self, value):
        self._sendSetValue = value

    def getSendSetValue(self):
        return self._sendSetValue

    sendSetValue = QtCore.Property(bool, getSendSetValue, setSendSetValue)

    def setMouseSensibility(self, value):
        self._mouseSensibility = value

    def getMouseSensibility(self):
        return self._mouseSensibility

    mouseSensibility = QtCore.Property(float, getMouseSensibility, setMouseSensibility)

    # intern

    def setInitValue(self):
        if not self._initialized:
            # il faut avant s'assurer que n'a pas été intialisé par deserialisation
            self.setValue(self._initValue)

    def tabletEvent(self, event):
        if event.type() == QtCore.QEvent.TabletMove and event.pressure() > 0.0:
            newY = event.globalPosF().y()
            if self._oldY is not None:
                deltaY = newY - self._oldY
                # *self.singleStep()):
                self._decValue -= deltaY * self._mouseSensibility
                QtWidgets.QSpinBox.setValue(
                    self, self._intValue + int(self._decValue) * self.singleStep()
                )
            self._oldY = newY

        elif event.type() == QtCore.QEvent.TabletPress:
            self._decValue = 0
            self._intValue = self.value
            self._oldY = event.globalPosF().y()
            # self.setCursor( QtGui.QCursor(QtCore.Qt.BlankCursor))

        elif event.type() == QtCore.QEvent.TabletRelease:
            pass
            # self.setCursor( QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def eventFilter(self, obj, event):
        eventType = event.type()
        if eventType == QtCore.QEvent.TouchBegin:
            print("useTouchScreen")
            self._useTouchScreen = True
            self._lineEdit.setReadOnly(True)  # permet de cacher le curseur clignotant
            event.accept()
            return True
        if eventType == QtCore.QEvent.MouseMove:
            if event.buttons():
                # permet limiter erreures des mouvemenent de tablette Wacom qui passent dans evenements de souris
                self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
                if self._oldY is not None:
                    # idem que  newY = event.globalPos().y() :
                    newY = QtGui.QCursor.pos().y()
                    deltaY = newY - self._oldY
                    # *self.singleStep()):
                    self._decValue -= deltaY * self._mouseSensibility
                    QtWidgets.QSpinBox.setValue(
                        self, self._intValue + int(self._decValue) * self.singleStep()
                    )
                    if not self._useTouchScreen:
                        # ne marche pas sur pipo quand utilise le doigt....:
                        QtGui.QCursor.setPos(self._oldX, self._oldY)
                self._oldY = QtGui.QCursor.pos().y()
                event.accept()
                return True
        elif eventType == QtCore.QEvent.MouseButtonRelease:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            event.accept()
            return True
        elif eventType == QtCore.QEvent.MouseButtonPress:
            self._oldX = QtGui.QCursor.pos().x()
            self._oldY = QtGui.QCursor.pos().y()
            self._decValue = 0
            self._intValue = self.value
            event.accept()
            return True
        return False

    # synchronisation

    def setSyncModule(self, value):
        self._sync.syncModule = value

    def getSyncModule(self):
        return self._sync.syncModule

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        self._sync.syncName = value

    def getSyncName(self):
        return self._sync.syncName

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        self._sync.save = value

    def getSyncSave(self):
        return self._sync.save

    syncSave = QtCore.Property(bool, getSyncSave, setSyncSave)

    # serialization

    def setSerialize(self, value):
        self._serialize = value

    def getSerialize(self):
        return self._serialize

    serialize = QtCore.Property(bool, getSerialize, setSerialize)

    def __getstate__(self):
        if self._serialize:
            return {"value": self.value}

    # IL FAUT LE LESSER A LA FIN CAR QT DESIGNER INITIALIZE LES PROPRIETES DANS L'ORDRE DU CODE!! ET IL FAUT INITIALISATION APRES AVOIR REDEFINI MIN ET MAX !
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setValue(self, value):
        if (not self._sendSetValue) or (
            not self._initialized and not self._sendInitValue
        ):
            blockSignal = True
            # print('blockSignal')
        else:
            blockSignal = False

        # permet de dire qu'il ne faut plus initialiser si on a déjà initialisé avec deserialisation:
        self._initialized = True
        if value == QtWidgets.QSpinBox.value(self) and self._repeat:
            if not blockSignal:
                self.valueChanged.emit(value)
        else:
            if not blockSignal:
                QtWidgets.QSpinBox.setValue(self, value)
            else:
                self.blockSignals(True)
                QtWidgets.QSpinBox.setValue(self, value)
                self.blockSignals(False)

    value = QtCore.Property(int, QtWidgets.QSpinBox.value, setValue)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = NumberUI()
    widget.show()
    app.exec_()
