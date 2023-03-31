# -*- coding: utf-8 -*-
"""
Created on Mon Dec 05 17:28:53 2016

@author: Baptiste
"""
import sys
import traceback
from qtpy import QtGui, QtWidgets


def exceptionDialog(exc_type, exc_value, exc_traceback):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    qapp = QtWidgets.QApplication.instance()
    if qapp is None:
        qapp = QtWidgets.QApplication(sys.argv)
    # permet de copier text d'une fenetre d'erreure
    qapp.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")
    msg = "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    QtWidgets.QMessageBox.critical(
        None,
        "Critical Error",
        "An unexpected Exception has occured!\n%s" % msg,
        QtWidgets.QMessageBox.Ok,
        QtWidgets.QMessageBox.NoButton,
    )


sys.excepthook = exceptionDialog
