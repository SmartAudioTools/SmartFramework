# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from time import perf_counter


class Fps(QtCore.QObject):
    def __init__(self, parent=None):
        super(Fps, self).__init__(parent)
        # self.numberEmbed.setGeometry(0,0,50,22)
        self.a = 0.03
        self.t_last = None
        self.smothInterval = None

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
            fps = 1.0 / self.smothInterval
            # print(fps)
            self.outFps.emit(fps)
        else:
            self.t_last = t


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Fps()
    app.exec_()
