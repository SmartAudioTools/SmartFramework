# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 13:43:50 2019

@author: Baptiste
"""
import os

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
from qtpy import QtCore, QtGui, QtWidgets

import sys

app = QtWidgets.QApplication(sys.argv)
widget = QtWidgets.QLineEdit()
widget.show()
app.exec_()
