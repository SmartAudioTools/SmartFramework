# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from time import perf_counter


class FpsUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.doubleSpinBox = QtWidgets.QSpinBox(self)
        self.doubleSpinBox.setMaximum(1000)
        self.doubleSpinBox.setReadOnly(True)
        self.doubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.doubleSpinBox.setKeyboardTracking(False)
        self.doubleSpinBox.setGeometry(QtCore.QRect(0, 0, 60, 30))
        self.outFps.connect(self.doubleSpinBox.setValue)
        self.a = 0.03
        self.t_last = None
        self.smothInterval = None
        self.lastFps = None

    # signaux

    outFps = QtCore.Signal(float)

    # slots

    @QtCore.Slot()
    @QtCore.Slot(object)
    def inImage(self, image=None):
        t = perf_counter()
        if self.t_last:
            interval = t - self.t_last
            self.t_last = t
            if self.smothInterval:
                self.smothInterval = interval * self.a + self.smothInterval * (
                    1.0 - self.a
                )
            else:
                self.smothInterval = interval
            fps = round(1.0 / self.smothInterval)
            if self.lastFps != fps:
                self.outFps.emit(fps)
                self.lastFps = fps
        else:
            self.t_last = t

    def sizeHint(self):
        return QtCore.QSize(60, 30)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = FpsUI()
    widget.show()
    app.exec_()
