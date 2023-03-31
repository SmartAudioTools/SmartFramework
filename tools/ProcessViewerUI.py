# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 14:19:24 2018

@author: Baptiste
"""
from SmartFramework.tools.process import process_iter

from qtpy import QtGui, QtWidgets
from qtpy.QtCore import Qt


class ProcessViewerUI(QtWidgets.QTreeWidget):
    def __init__(self, parent=None, sortingEnabled=True):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.setColumnCount(2)
        # self.header().close()
        for process in process_iter():
            processItem = QtWidgets.QTreeWidgetItem(self)
            processItem.setText(0, process.name())
            description = process.description()
            if description:
                # print(description)
                processItem.setText(1, description)
        self.sortByColumn(0, Qt.AscendingOrder)


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ProcessViewerUI()
    widget.show()
    app.exec_()
