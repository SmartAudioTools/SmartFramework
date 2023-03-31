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
        print("Trackpad INIT !!!")
        # hack pour debuger clic droit du Trackpad du macbook pro
        self._trackpadPressingRight = False
        self._trackpadPressingLeft = False
        self._trackpadFakeLeft = False
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        eventType = event.type()
        # hack pour debuger clic droit du Trackpad du macbook pro
        # print(eventNames[eventType])
        if eventType == QtCore.QEvent.MouseMove:
            if (
                self._trackpadPressingLeft
                and self._trackpadPressingRight
                and event.buttons() != (QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
            ):
                event.buttons = QtCore.Qt.LeftButton | QtCore.Qt.RightButton
            elif self._trackpadPressingLeft and event.buttons() != QtCore.Qt.LeftButton:
                event.buttons = lambda: QtCore.Qt.LeftButton
            elif (
                self._trackpadPressingRight and event.buttons() != QtCore.Qt.RightButton
            ):
                event.buttons = lambda: QtCore.Qt.RightButton
        if eventType in (
            QtCore.QEvent.MouseButtonPress,
            QtCore.QEvent.MouseButtonDblClick,
        ):
            if event.button() == QtCore.Qt.LeftButton:
                if debug:
                    print("\nMPL", end=" ")
                if self._trackpadPressingRight:
                    self._trackpadFakeLeft = True
                    return True
                else:
                    self._trackpadPressingLeft = True
            if event.button() == QtCore.Qt.RightButton:
                if self._trackpadPressingRight:
                    return True
                else:
                    self._trackpadPressingRight = True
        if eventType == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton:
                if debug:
                    print("\nMRL", end=" ")
                if self._trackpadFakeLeft:
                    self._trackpadFakeLeft = False
                    oldButton = event.button
                    event.button = (
                        lambda: QtCore.Qt.RightButton
                    )  # fou la merde pour les evenemnt suivant , car il semble recycler
                    obj.mouseReleaseEvent(event)
                    # QtWidgets.QApplication.sendEvent(QtWidgets.QApplication.instance().topLevelWidgets()[0],event)
                    # obj.event(event) # NE MARCHE PAS TOUJOURS L'EVENEMENT PAS TOUJOURS PRIS EN CHARGE !?
                    event.button = oldButton
                    self._trackpadPressingRight = False
                    return True

                else:
                    self._trackpadPressingLeft = False
            if event.button() == QtCore.Qt.RightButton:
                if debug:
                    print("\nMRR", end=" ")
                if not self._trackpadPressingRight or self._trackpadFakeLeft:
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
        # fou la merde pour les evenemnt suivant , car il semble recycler
        event.button = lambda: QtCore.Qt.RightButton
        obj.mouseReleaseEvent(event)
        # QtWidgets.QApplication.sendEvent(QtWidgets.QApplication.instance().topLevelWidgets()[0],event)
        # obj.event(event) # NE MARCHE PAS TOUJOURS L'EVENEMENT PAS TOUJOURS PRIS EN CHARGE !?
        event.button = oldButton


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
