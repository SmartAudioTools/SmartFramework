# -*- coding: utf-8 -*-
"""
Created on Fri
 Sep 26 13:34:47 2014

@author: Baptiste
"""
import sys
from qtpy import QtGui, QtWidgets, QtCore
from SmartFramework.tools.dictionaries import reverseDict

eventNames = reverseDict(QtCore.QEvent.__dict__)
# print("\n".join(sorted( eventNames.values())))


if __name__ == "__main__":
    baseClass = QtWidgets.QWidget
    debug = True
else:
    baseClass = object
    debug = False


class Trackpad(baseClass):
    def __init__(self, parent=None):
        baseClass.__init__(self)
        # print("Trackpad INIT !!!")
        # hack pour debuger clic droit du Trackpad du macbook pro
        self._trackpadLeftPressTimer = QtCore.QTimer()
        self._trackpadLeftPressTimer.setInterval(1)
        self._trackpadLeftPressTimer.timeout.connect(self.trackpadSheduledLeftPress)
        self._trackpadLeftPressTimer.setSingleShot(True)
        self._trackpadLeftReleaseTimer = QtCore.QTimer()
        self._trackpadLeftReleaseTimer.setInterval(1)
        self._trackpadLeftReleaseTimer.timeout.connect(
            self.trackpadSheduledRightRelease
        )
        self._trackpadLeftReleaseTimer.setSingleShot(True)
        self._trackpadPressingRight = False
        self._trackpadPressingLeft = False
        self._eventToRestore = None
        self.installEventFilter(self)
        # self.setMouseTracking(True)

    def restoreMouseMoveEventButtons(self):
        event, buttons = self._eventToRestore
        event.buttons = buttons
        self._eventToRestore = None

    def eventFilter(self, obj, event):
        eventType = event.type()
        # hack pour debuger clic droit du Trackpad du macbook pro
        # print(eventNames[eventType])

        if eventType == QtCore.QEvent.MouseMove:
            if self._trackpadPressingLeft and self._trackpadPressingRight:
                if event.buttons() != (QtCore.Qt.LeftButton | QtCore.Qt.RightButton):
                    self._eventToRestore = (event, event.buttons)
                    event.buttons = (
                        lambda: QtCore.Qt.LeftButton | QtCore.Qt.RightButton
                    )  # fou la merde pour les mouveMouve events avec mouse tracking (sans boutons enfoncés) , car il semble recycler, du coup je schedule une restauration de la methode buttons()
                    QtCore.QTimer.singleShot(0, self.restoreMouseMoveEventButtons)
            elif self._trackpadPressingLeft:
                if event.buttons() != QtCore.Qt.LeftButton:
                    self._eventToRestore = (event, event.buttons)
                    event.buttons = (
                        lambda: QtCore.Qt.LeftButton
                    )  # fou la merde pour les mouveMouve events avec mouse tracking (sans boutons enfoncés) , car il semble recycler, du coup je schedule une restauration de la methode buttons()
                    QtCore.QTimer.singleShot(0, self.restoreMouseMoveEventButtons)
            elif self._trackpadPressingRight:
                if event.buttons() != QtCore.Qt.RightButton:
                    self._eventToRestore = (event, event.buttons)
                    event.buttons = (
                        lambda: QtCore.Qt.RightButton
                    )  # fou la merde pour les mouveMouve events avec mouse tracking (sans boutons enfoncés) , car il semble recycler, du coup je schedule une restauration de la methode buttons()
                    QtCore.QTimer.singleShot(0, self.restoreMouseMoveEventButtons)
        elif eventType in (
            QtCore.QEvent.MouseButtonPress,
            QtCore.QEvent.MouseButtonDblClick,
        ):
            if event.button() == QtCore.Qt.LeftButton:
                if debug:
                    print("\nMPL", end=" ")
                if self._trackpadPressingRight:
                    self._trackpadLeftPressTimer.start()
                    self._lastLeftPressObjAndEvent = (obj, event)
                    return True
                else:
                    self._trackpadPressingLeft = True
            if event.button() == QtCore.Qt.RightButton:
                if debug:
                    print("\nMPR", end=" ")
                self._trackpadLeftReleaseTimer.stop()
                if self._trackpadPressingRight:
                    event.accept()
                    return True
                else:
                    self._trackpadPressingRight = True
        elif eventType == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton:
                if debug:
                    print("\nMRL", end=" ")
                if not self._trackpadPressingLeft:
                    self._lastLeftReleaseObjAndEvent = (obj, event)
                    self._trackpadLeftReleaseTimer.start()
                    return True
                else:
                    self._trackpadPressingLeft = False
            if event.button() == QtCore.Qt.RightButton:
                if debug:
                    print("\nMRR", end=" ")
                if self._trackpadLeftPressTimer.isActive():
                    self._trackpadLeftPressTimer.stop()
                    event.accept()
                    return True
                else:
                    self._trackpadPressingRight = False
        return False

    def trackpadSheduledRightRelease(self):
        if debug:
            print("\ntrackpadSheduledRightRelease", end=" ")
        self._trackpadPressingRight = False
        obj, event = self._lastLeftReleaseObjAndEvent
        oldButton = event.button
        # fou la merde pour les evenemnt suivant , car il semble recycler :
        event.button = lambda: QtCore.Qt.RightButton
        obj.mouseReleaseEvent(event)
        # QtWidgets.QApplication.sendEvent(QtWidgets.QApplication.instance().topLevelWidgets()[0],event)
        # obj.event(event) # NE MARCHE PAS TOUJOURS L'EVENEMENT PAS TOUJOURS PRIS EN CHARGE !?
        event.button = oldButton

    def trackpadSheduledLeftPress(self):
        # hack pour debuger clic droit du Trackpad du macbook pro
        self._trackpadPressingLeft = True
        if debug:
            print(
                "\nself._trackpadPressingLeft = True in trackpadSheduledLeftPress",
                end=" ",
            )
        obj, event = self._lastLeftPressObjAndEvent
        obj.mousePressEvent(event)
        # QtWidgets.QApplication.sendEvent(QtWidgets.QApplication.instance().topLevelWidgets()[0],event)
        # QtWidgets.QApplication.sendEvent(QtWidgets.QApplication.instance(),event)
        # obj.event(event) # NE MARCHE PAS TOUJOURS L'EVENEMENT PAS TOUJOURS PRIS EN CHARGE !?


class MousseTest(Trackpad):
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print("\nmousePressLeft!", end=" ")
        elif event.button() == QtCore.Qt.RightButton:
            print("\nmousePressRight!", end=" ")

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            print("\nmouseReleaseRight", end=" ")
        elif event.button() == QtCore.Qt.LeftButton:
            print("\nmouseReleaseLeft", end=" ")

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            print("r", end=" ")
        elif event.buttons() == QtCore.Qt.LeftButton:
            print("l", end=" ")
        else:
            print("m", end=" ")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MousseTest()
    win.show()
    # app.installEventFilter(win)
    app.exec_()
