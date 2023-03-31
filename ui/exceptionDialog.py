# -*- coding: utf-8 -*-
"""
Created on Mon Dec 05 17:28:53 2016

@author: Baptiste
"""
import sys
import traceback
from qtpy import QtWidgets, QtCore


class ExceptionDialog(QtCore.QObject):

    outMessage = QtCore.Signal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.outMessage.connect(self.inMessage)

    @QtCore.Slot(str)
    def inMessage(self, message):
        qapp = QtWidgets.QApplication.instance()
        if qapp is None:
            qapp = QtWidgets.QApplication(sys.argv)
        # permet de copier text d'une fenetre d'erreure
        qapp.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

        QtWidgets.QMessageBox.critical(
            None,
            "Critical Error",
            "An unexpected Exception has occured!\n%s" % message,
            QtWidgets.QMessageBox.Ok,
            QtWidgets.QMessageBox.NoButton,
        )

    def showDialog(self, exc_type, exc_value, exc_traceback):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        msg = "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.outMessage.emit(msg)


exceptionDialog = ExceptionDialog()
sys.excepthook = exceptionDialog.showDialog
