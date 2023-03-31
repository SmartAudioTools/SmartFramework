from qtpy import QtCore, QtGui, QtWidgets
import cv2
import numpy as np

DEBUG = False


class Window(QtCore.QObject):

    # constructor -----------

    def __init__(self, parent=None, name="Window", open=True):
        QtCore.QObject.__init__(self, parent)
        self.name = name
        self._open = False
        if open:
            self.setOpen(open)
        QtWidgets.QApplication.instance().lastWindowClosed.connect(self.__del__)
        if DEBUG:
            print("dans window init :" + str(QtCore.QThread.currentThread()))

    # slots -------------------

    @QtCore.Slot()
    @QtCore.Slot(bool)
    def setOpen(self, b=True):
        if b:
            if not self._open:
                self._open = True
                cv2.namedWindow(self.name, 1)  # cv2.WINDOW_NORMAL
        else:
            self.close()

    @QtCore.Slot(object)
    def inImage(self, img):
        if DEBUG:
            print("dans window :" + str(QtCore.QThread.currentThread()))
        if self._open:
            cv2.imshow(self.name, np.copy(img))

    # methodes ----------------

    def __del__(self):
        QtWidgets.QApplication.instance().lastWindowClosed.disconnect(self.__del__)
        QtCore.QTimer.singleShot(0, self.close)

    def close(self):
        if self._open:
            self._open = False
            cv2.destroyWindow(self.name)


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = Window()
    app.exec_()
