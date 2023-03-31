# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from time import perf_counter
import numpy as np

# import matplotlib.pyplot as plt


class TimeMonitor(QtCore.QObject):
    # constructor

    def __init__(self, parent=None):
        super(TimeMonitor, self).__init__(parent)
        self.listeClock = []
        self.recording = False
        # import matplotlib.pyplot as plt

    # slots

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def inTime(self, t):
        if self.recording:
            self.listeClock.append(t)

    @QtCore.Slot()
    def inTick(self):
        if self.recording:
            t = perf_counter()
            self.listeClock.append(t)

    @QtCore.Slot()
    def start(self):
        del self.listeClock
        self.listeClock = []
        self.recording = True

    @QtCore.Slot()
    def stop(self):
        self.recording = False

    @QtCore.Slot(bool)
    def startStop(self, b):
        if b:
            self.start()
        else:
            self.stop()

    @QtCore.Slot()
    def plotIntervals(self):
        arrayClock = np.array(self.listeClock) * 1000.0
        arrayIntevals = np.diff(arrayClock)
        plt.plot(arrayIntevals, ",")
        plt.show()

    @QtCore.Slot()
    def plotHistogram(self):
        arrayClock = np.array(self.listeClock) * 1000.0
        arrayIntevals = np.diff(arrayClock)
        datas, bins, patches = plt.hist(arrayIntevals, 100)
        plt.show()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = TimeMonitor()
    app.exec_()
