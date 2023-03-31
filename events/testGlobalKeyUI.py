# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.events.GlobalKey import GlobalKey


class TestGlobalKeyUI(QtWidgets.QWidget):

    # constructor

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.globalkey = GlobalKey(self)
        self.layoutWidget = QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.gridLayout.addWidget(self.spinBox, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(self.layoutWidget)
        self.gridLayout.addWidget(self.spinBox_2, 0, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout.addWidget(self.label_3, 0, 3, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.layoutWidget)
        self.gridLayout.addWidget(self.lineEdit_2, 1, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout.addWidget(self.label_4, 1, 3, 1, 1)
        self.label.setText("KeyID")
        self.label_3.setText("Ascii Int")
        self.label_2.setText("Key")
        self.label_4.setText("Ascii Chr")

        # connexions
        self.globalkey.Ascii[int].connect(self.spinBox_2.setValue)
        self.globalkey.Ascii[str].connect(self.lineEdit_2.setText)
        self.globalkey.Key[str].connect(self.lineEdit.setText)
        self.globalkey.KeyID[int].connect(self.spinBox.setValue)

        # geometry
        self.resize(391, 94)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 361, 71))


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = TestGlobalKeyUI()
    widget.setWindowTitle(os.path.splitext(os.path.split(__file__)[1])[0])
    widget.show()
    app.exec_()
