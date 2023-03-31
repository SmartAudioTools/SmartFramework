# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.events.GlobalMouse import GlobalMouse


class TestGlobalMouseUI(QtWidgets.QWidget):

    # constructor

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.globalmouse = GlobalMouse(self)
        self.layoutWidget = QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.spinBox.setMinimum(-99999)
        self.spinBox.setMaximum(99999)
        self.gridLayout.addWidget(self.spinBox, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(self.layoutWidget)
        self.spinBox_2.setMinimum(-99999)
        self.spinBox_2.setMaximum(99999)
        self.gridLayout.addWidget(self.spinBox_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)
        self.spinBox_3 = QtWidgets.QSpinBox(self.layoutWidget)
        self.spinBox_3.setMinimum(-99999)
        self.spinBox_3.setMaximum(9999)
        self.gridLayout.addWidget(self.spinBox_3, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 1)
        self.label.setText("x")
        self.label_3.setText("y")
        self.label_4.setText("Wheel")

        # connexions
        self.globalmouse.PositionX[int].connect(self.spinBox.setValue)
        self.globalmouse.PositionY[int].connect(self.spinBox_2.setValue)
        self.globalmouse.Wheel[int].connect(self.spinBox_3.setValue)

        # geometry
        self.resize(198, 270)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 33, 177, 125))


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = TestGlobalMouseUI()
    widget.setWindowTitle(os.path.splitext(os.path.split(__file__)[1])[0])
    widget.show()
    app.exec_()
