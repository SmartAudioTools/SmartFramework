# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 14:19:24 2018

@author: Baptiste
"""

from qtpy import QtGui, QtWidgets
from qtpy.QtCore import Qt
import psutil


class ServicesViewerUI(QtWidgets.QTreeWidget):
    def __init__(self, parent=None, sortingEnabled=True):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.setColumnCount(4)
        headers = ["display_name", "status", "start_type", "description"]
        self.setHeaderLabels(["Name", "Status", "Start type", "Description"])
        # self.header().close()
        grey = QtGui.QColor(175, 175, 175)
        for service in psutil.win_service_iter():
            serviceItem = QtWidgets.QTreeWidgetItem(self)
            serviceDict = service.as_dict()
            stopped = serviceDict["status"] == "stopped"
            for column, header in enumerate(headers):
                serviceItem.setText(column, serviceDict[header])
                if stopped:
                    serviceItem.setForeground(column, grey)

        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ServicesViewerUI()
    widget.show()
    app.exec_()
