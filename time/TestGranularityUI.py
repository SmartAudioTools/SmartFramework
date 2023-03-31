# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.time.QtTimer import QtTimer
from SmartFramework.time.TimeMonitorUI import TimeMonitorUI


class TestGranularityUI(QtWidgets.QWidget):

    # constructor

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.qttimer = QtTimer(self, interval=1)
        self.timemonitorui = TimeMonitorUI(self)

        # connexions
        self.qttimer.output.connect(self.timemonitorui.inTick)

        # geometry
        self.resize(451, 43)
        self.timemonitorui.setGeometry(QtCore.QRect(0, 0, 451, 41))


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = TestGranularityUI()
    widget.setWindowTitle(os.path.splitext(os.path.split(__file__)[1])[0])
    widget.show()
    app.exec_()
