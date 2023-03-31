from qtpy import QtCore, QtGui, QtWidgets
from time import perf_counter
import numpy as np

# import matplotlib.pyplot as plt


class TimeMonitorUI(QtWidgets.QWidget):
    pass

    # constructor

    def __init__(self, parent=None, nbClocks=1):
        QtWidgets.QWidget.__init__(self, parent)
        self.recording = False
        self.nbClocks = nbClocks
        self.listeClock = []
        self.reset()
        # ajout pour interface graphique
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setText("Intervals")
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setText("Histogram")
        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setText("Start/Stop")

        # geometry
        self.resize(450, 40)
        self.checkBox.setGeometry(QtCore.QRect(0, 0, 140, 40))
        self.pushButton.setGeometry(QtCore.QRect(150, 0, 150, 40))
        self.pushButton_2.setGeometry(QtCore.QRect(300, 0, 150, 40))

        # connexions
        self.checkBox.toggled[bool].connect(self.startStop)
        self.pushButton.pressed.connect(self.plotIntervals)
        self.pushButton_2.pressed.connect(self.plotHistogram)

    # signaux

    outRunning = QtCore.Signal(bool)
    outStart = QtCore.Signal()
    outStop = QtCore.Signal()

    # slots

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def inTime(self, t):
        if self.recording:
            self.listeClock[0].append(t)

    @QtCore.Slot()
    # @QtCore.Slot(object)
    def inTick(self):
        if self.recording:
            t = perf_counter()
            self.listeClock[0].append(t)

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def inTime2(self, t):
        if self.recording:
            self.listeClock[1].append(t)

    @QtCore.Slot()
    # @QtCore.Slot(object)
    def inTick2(self):
        if self.recording:
            t = perf_counter()
            self.listeClock[1].append(t)

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def inTime3(self, t):
        if self.recording:
            self.listeClock[2].append(t)

    @QtCore.Slot()
    # @QtCore.Slot(object)
    def inTick3(self):
        if self.recording:
            t = perf_counter()
            self.listeClock[2].append(t)

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def inTime4(self, t):
        if self.recording:
            self.listeClock[3].append(t)

    @QtCore.Slot()
    # @QtCore.Slot(object)
    def inTick4(self):
        if self.recording:
            t = perf_counter()
            self.listeClock[3].append(t)

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def inTime5(self, t):
        if self.recording:
            self.listeClock[4].append(t)

    @QtCore.Slot()
    # @QtCore.Slot(object)
    def inTick5(self):
        if self.recording:
            t = perf_counter()
            self.listeClock[4].append(t)

    @QtCore.Slot()
    def start(self):
        self.reset()
        self.recording = True
        self.outStart.emit()
        self.outRunning.emit(True)

    @QtCore.Slot()
    def stop(self):
        self.recording = False
        self.outStop.emit()
        self.outRunning.emit(False)

    @QtCore.Slot(bool)
    def startStop(self, b):
        if b:
            self.start()
        else:
            self.stop()

    @QtCore.Slot()
    def plotIntervals(self):
        self.makeArrays()
        for i in range(self.nbClocks):
            plt.subplot(1, self.nbClocks, i + 1)
            plt.title(str(i))
            plt.plot(self.arrayIntevals[i], ",")
        plt.show()

    @QtCore.Slot()
    def plotHistogram(self):
        self.makeArrays()
        for i in range(self.nbClocks):
            plt.subplot(1, self.nbClocks, i + 1)
            datas, bins, patches = plt.hist(self.arrayIntevals[i], 100)
        plt.show()

    def makeArrays(self):
        self.arrayClock = []
        self.arrayIntevals = []
        for i in range(self.nbClocks):
            arrayClock = np.array(self.listeClock[i]) * 1000.0
            self.arrayClock.append(arrayClock)
            self.arrayIntevals.append(np.diff(arrayClock))

    def reset(self):
        del self.listeClock
        self.listeClock = []
        for i in range(self.nbClocks):
            self.listeClock.append([])


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = TimeMonitorUI()
    widget.show()
    app.exec_()
