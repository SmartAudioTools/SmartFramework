# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from time import perf_counter


class IntervalMeanUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.spinBox = QtWidgets.QDoubleSpinBox(self)
        self.spinBox.setGeometry(0, 0, 80, 22)
        self.outFps.connect(self.spinBox.setValue)
        self.a = 0.01
        self.t_last = None
        self.smothInterval = None

    # signaux

    outFps = QtCore.Signal(float)

    # slots

    @QtCore.Slot()
    @QtCore.Slot(object)
    def inImage(self, image=None):
        if self.t_last:
            t = perf_counter()
            interval = t - self.t_last
            self.t_last = t
            if self.smothInterval:
                self.smothInterval = interval * self.a + self.smothInterval * (
                    1.0 - self.a
                )
            else:
                self.smothInterval = interval
            # print(fps)
            self.outFps.emit(self.smothInterval * 1000.0)
        else:
            self.t_last = perf_counter()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = IntervalMeanUI()
    widget.show()
    app.exec_()
