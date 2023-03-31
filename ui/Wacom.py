# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 13:34:47 2014

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


class Wacom(baseClass):
    def __init__(self, parent=None):
        baseClass.__init__(self)
        # Object.__init__(self,parent)
        # self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents)
        # self.setAttribute(QtCore.Qt.WA_InputMethodEnabled)
        # self._tabletTimer = QtCore.QTimer()
        # self._tabletTimer.timeout.connect(self.tabletEventTimeOut)
        # self._tabletTimer.setSingleShot(True)
        # self._tabletTimerRunning = False
        # self._tabletLastPosHi   = None
        self._tabletUse = False
        # self._tabletRight = False
        self._tabletButton = 0
        self._MouseButtonDblClicking = False
        self._tabletAlreadyPressed = False
        self._tabletLastIsPressOrRelease = False
        self._lastEventType = None
        # pour filtrer les mouse move quand utilise le radia menu de la Wacom :
        self._lastEventTypeDiffM = None
        self._beforelastEventType = None
        self._tabletLastPosHi = QtCore.QPointF()
        # self.setAttribute(QtCore.Qt.WA_StaticContents)
        ##def eventFilter(self,event) :

    # a réimplementé dans la classe heritante --------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print("\nmousePressLeft!", end=" ")
        elif event.button() == QtCore.Qt.RightButton:
            print("\nmousePressRight!", end=" ")

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print("\nmouseReleaseLeft", end=" ")
        elif event.button() == QtCore.Qt.RightButton:
            print("\nmouseReleaseRight", end=" ")

    def mouseMoveEvent(self, event):
        print("m", end=" ")

    def wheelEvent(self, event):

        # if event.button()== QtCore.Qt.MiddleButton :
        #    pass
        # else :
        # print("wheel delta : " ,event.angleDelta().y())
        event.accept()

    def tabletEvent(self, event):

        # print(event.pointerType()        if QtGui.QTabletEvent.Eraser)
        if event.type() == QtCore.QEvent.TabletMove:
            pass
            # print('.',)
        elif event.type() == QtCore.QEvent.TabletPress:
            if event.button() == QtCore.Qt.LeftButton:
                print("\ntabletPressLeft", end=" ")
            elif event.button() == QtCore.Qt.RightButton:
                print("\ntabletPressRight", end=" ")
            print("\ntabletPointerType : " + str(event.pointerType()))

        elif event.type() == QtCore.QEvent.TabletRelease:
            if event.button() == QtCore.Qt.LeftButton:
                print("\ntabletReleaseLeft", end=" ")
            elif event.button() == QtCore.Qt.RightButton:
                print("\ntabletReleaseRight", end=" ")
        else:
            print(event.type())

    def touchEvent(self, event):
        pass
        print("t", end=" ")
        # event.accept()

    def shortcutOverrideEvent(self, event):
        print("ShortcutOverride!")

    def keyPressEvent(self, event):
        print("wacom ----------")
        print("event.key() : ", hex(int(event.key())))
        print("event.text() : ", event.text())
        print("event.text().encode('ascii') : ", event.text().encode("ascii"))
        print("event.nativeModifiers() : ", hex(int(event.nativeModifiers())))
        print("event.modifiers() : ", hex(int(event.modifiers())))
        print(event.nativeScanCode())
        print(event.nativeVirtualKey())

    # HACK en attendant Qt 5.4 ------------------------------------------------

    def tabletMoveMouseEvent(self, event):
        # mouvement de stylot traduit en mouvement de souris
        pass

    def checkTouch(self):
        if not self._tabletUse:
            # HACK permetant de tracker les mouvement d'un doigt sur tablette
            self.setMouseTracking(True)
            self._tabletUse = True

    def event(self, event):

        # print("wacom recoit un evt !")
        eventType = event.type()
        if eventType != QtCore.QEvent.MouseMove:
            self._lastEventTypeDiffM = eventType
        if (
            debug
            and eventType in eventNames
            and eventType != QtCore.QEvent.TabletMove
            and eventType != QtCore.QEvent.MouseMove
        ):
            print("\n", eventNames[eventType], end=" ")
            pass
        if eventType == QtCore.QEvent.TabletMove:
            if debug:
                print(",", end=" ")
            self._tabletLastPosHi = event.globalPosF()
            if type(event) != QtGui.QTabletEvent:
                raise Exception("\nBUG")
            self.checkTouch()
            self._tabletLastIsPressOrRelease = False  # utile ?
            self.tabletEvent(event)
        elif eventType == QtCore.QEvent.TabletPress:
            if type(event) != QtGui.QTabletEvent:
                raise Exception("\nBUG!")
            if event.pointerType() == QtGui.QTabletEvent.Eraser:
                # self._tabletButton =  QtCore.Qt.LeftButton
                event.button = lambda: QtCore.Qt.LeftButton
                self._tabletButton = QtCore.Qt.LeftButton
                self.tabletEvent(
                    event
                )  # on declanche immediatemnt car aura du mal à recuperer le pointerType dans evenement souris

            else:
                self._tabletLastIsPressOrRelease = True
                # indispensable pour recuperer click de souris et savoir quel bouton a été cliqué sur stylot                 # HACK en attendant Qt 5.4:
                event.ignore()
                # self.setMouseTracking(False)
                # commence à traqer tablette en dehors de la zone
                # => faut la merder pour deplacer fenetre

        elif eventType == QtCore.QEvent.TabletRelease:
            if type(event) != QtGui.QTabletEvent:
                raise Exception("\nBUG")
            self._tabletAlreadyPressed = False
            self._tabletLastIsPressOrRelease = True
            event.button = lambda: self._tabletButton
            self.tabletEvent(
                event
            )  # on declanche immediatemnt car aura du mal à recuperer le pointerType dans evenement souris
            if not event.pointerType() == QtGui.QTabletEvent.Eraser:
                #  obligé de redeclancher bouton souris sinon le fou la merde pour deplacer fenetre si ignore le click et ignore le relachement:
                event.ignore()

        elif eventType == QtCore.QEvent.MouseButtonPress:
            if self._tabletLastIsPressOrRelease:
                if not self._tabletAlreadyPressed:
                    self._tabletAlreadyPressed = True
                    self._tabletButton = event.button()
                    event.type = lambda: QtCore.QEvent.TabletPress
                    event.pointerType = lambda: QtGui.QTabletEvent.Pen
                    self.tabletEvent(event)
            else:
                # print("\nNot TabletEvent")
                self.mousePressEvent(event)

        elif eventType == QtCore.QEvent.MouseButtonRelease:
            if self._MouseButtonDblClicking:
                self._MouseButtonDblClicking = False
            else:
                # if self.isTabletEvent(event):
                if (
                    not self._tabletLastIsPressOrRelease
                ):  # on doit resortir le bouton stocké et non celui donnée par mousse.button , car si on clicke srur bouton stylot arpes l'avoir possé , Release bouton droit au lieu du gauche
                    self.mouseReleaseEvent(event)

        elif eventType == QtCore.QEvent.MouseMove:
            # if self.isTabletEvent(event):
            if debug:
                print("m", end=" ")
            if self._tabletLastIsPressOrRelease:
                event.accept()
            else:

                diffPos = self._tabletLastPosHi - event.globalPos()
                if abs(diffPos.x() - 0.5) > 5.0 or abs(diffPos.y() - 0.5) > 5.0:
                    if (
                        event.buttons()
                    ):  #  permet de considerer le tracking de souris sans clic enclanché comme du mutli-touch
                        self.mouseMoveEvent(event)
                    elif (
                        self.isActiveWindow()
                        and self._lastEventType
                        not in [
                            QtCore.QEvent.TabletMove,
                            QtCore.QEvent.Enter,
                            QtCore.QEvent.CursorChange,
                            QtCore.QEvent.Paint,
                            QtCore.QEvent.CursorChange,
                            QtCore.QEvent.ToolTip,
                        ]
                        and self._beforelastEventType not in [QtCore.QEvent.Enter]
                        and self.rect().adjusted(0, 0, -1, -1).contains(event.pos())
                    ):  # hack pour considerer mouvement de souris comme des toucheEvent quand utiliser tablette...
                        if self._tabletUse:
                            # QtCore.QEvent.TabletMove :  pour eviter un saut quand sort le stylot verticalement et le remet ailleur
                            # print("\n",self._tabletLastPosHi,)
                            # if debug :  print('\n pos : ',event.pos(),'!!!!!!!!!!!!!!!!!!!!!!!',)
                            # if debug :  print( eventNames[self._beforelastEventType])
                            if debug:
                                print("\n diffpos :", diffPos, end=" ")
                            self.touchEvent(event)
                        else:
                            self.mouseMoveEvent(event)

        elif eventType == QtCore.QEvent.MouseButtonDblClick:  # bloc les doubles click
            self._MouseButtonDblClicking = True

        else:
            # if eventType in eventNames:
            #    print("\n",eventNames[eventType])
            QtWidgets.QWidget.event(self, event)
        self._beforelastEventType = self._lastEventType
        self._lastEventType = eventType
        return event.isAccepted()

    def isMouseMoveEvent(self, event):  # HACK en attendant Qt 5.3
        if self._tabletLastPosHi is not None:
            diffPos = self._tabletLastPosHi - event.globalPos()
            if abs(diffPos.x() - 0.5) < 0.6 and abs(diffPos.y() - 0.5) < 0.6:
                return False
        else:
            return True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Wacom()
    win.show()
    # app.installEventFilter(win)
    app.exec_()
