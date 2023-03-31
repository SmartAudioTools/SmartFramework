# -*- coding: utf-8 -*-
"""
Created on Mon Dec 05 17:28:53 2016

@author: Baptiste
"""
# lire https://docs.python.org/3.1/library/warnings.html
from qtpy import QtCore, QtGui


class digestWarningDialog(QtCore.QObject):
    def __init__(self, parent):
        self.warnings = []
        self.timer.setInterval(0)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.sheduledMessageBox)

    def warning(self, text):
        self.warnings.append(text)
        self.timer.start()

    def sheduledMessageBox(self):
        if self.warnings:
            QtWidgets.QApplication.instance().setStyleSheet(
                "QMessageBox { messagebox-text-interaction-flags: 5; }"
            )  # permet de copier text d'une fenetre d'erreure
            msg = "\n".join(self.warnings)
            QtWidgets.QMessageBox.critical(
                None,
                "Warning",
                msg,
                QtWidgets.QMessageBox.Ok,
                QtWidgets.QMessageBox.NoButton,
                QtWidgets.QMessageBox.NoButton,
            )
            self.warnings = []
