# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 12:14:18 2017

@author: Baptiste
"""

from qtpy import QtCore, QtGui, QtWidgets

eventNames = {value: key for key, value in QtCore.QEvent.__dict__.items()}
debug = False  # sera éventuellement écrasé dans if __name__ == "__main__":


class TouchUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)

    def event(self, event):
        eventType = event.type()
        # ignore tous les evenement de souris qui ont été synthetisé à partir d'un touchEvent
        if eventType in (
            QtCore.QEvent.MouseButtonPress,
            QtCore.QEvent.MouseButtonDblClick,
            QtCore.QEvent.MouseButtonRelease,
            QtCore.QEvent.MouseMove,
            QtCore.QEvent.Wheel,
        ):
            if event.source() == QtCore.Qt.MouseEventSynthesizedBySystem:
                event.ignore()
                return True
        if eventType == QtCore.QEvent.TouchBegin:
            globalPosition = event.touchPoints()[0].screenPos()
            if debug:
                print("TouchBegin", globalPosition)
            event.accept()  # utile ?
            return True
        elif eventType == QtCore.QEvent.TouchUpdate:
            if debug:
                print("TouchUpdate")
            event.accept()  # utile ?
            return True
        elif eventType == QtCore.QEvent.TouchEnd:
            if debug:
                print("TouchEnd")
            event.accept()  # utile ?
            return True
        return QtWidgets.QWidget.event(self, event)

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
    import sys

    debug = True
    app = QtWidgets.QApplication(sys.argv)
    widget = TouchUI()
    widget.resize(QtCore.QSize(500, 500))
    widget.show()
    app.exec_()
