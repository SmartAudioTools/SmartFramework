# -*- coding: utf-8 -*-
"""
Created on Wed May  4 14:15:52 2022

@author: Baptiste
"""
import sys
import os

# os.environ['QT_API'] = 'pyqt6'
os.environ["FORCE_QT_API"] = "pyqt6"
from qtpy import QtCore, QtGui, QtWidgets, API

# from qtpy import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv)
# widget = QtWidgets.QSpinBox() # pyqt6
# widget.setAlignment(QtCore.Qt.Alignment.AlignCenter) # marche avec pyqt6


# hack
print(API)
if API == "pyqt6":
    QtWidgets_QSpinBox_init_orignal = QtWidgets.QSpinBox.__init__

    def QtWidgets_QSpinBox_init(self, *args, **kargs):
        alignment = kargs.pop("alignment", None)
        QtWidgets_QSpinBox_init_orignal(self, *args, **kargs)
        if alignment is not None:
            self.setAlignment(alignment)

    QtWidgets.QSpinBox.__init__ = QtWidgets_QSpinBox_init


# widget = QtWidgets.QSpinBox()
# widget = QtWidgets.QSpinBox(alignment=QtCore.Qt.Alignment.AlignCenter)
# from PyQt5 : AttributeError: type object 'Alignment' has no attribute 'AlignCenter'
# from PyQt6 : TypeError: unable to convert a Python 'Alignment' object to a C++ 'Qt::Alignment' instance
# qtpy PyQt5 : AttributeError: type object 'Alignment' has no attribute 'AlignCenter'
# qtpy PyQt6 : TypeError: unable to convert a Python 'Alignment' object to a C++ 'Qt::Alignment' instance

widget = QtWidgets.QSpinBox(alignment=QtCore.Qt.AlignCenter)  #
# from PyQt5 : ok
# from PyQt6 : AttributeError: type object 'Qt' has no attribute 'AlignCenter'
# qtpy PyQt5 : ok
# qtpy PyQt6 : avec hack : OK ,  sans hack : TypeError: unable to convert a Python 'Alignment' object to a C++ 'Qt::Alignment' instance


widget.show()
app.exec()
