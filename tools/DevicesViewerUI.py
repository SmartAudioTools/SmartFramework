from qtpy import QtGui, QtWidgets
from devices import Devices


class DevicesViewerUI(QtWidgets.QTreeWidget, Devices):
    def __init__(self, parent=None, sortingEnabled=True):
        QtWidgets.QTreeWidget.__init__(self, parent)
        Devices.__init__(self)
        self.header().close()
        for classeName, devices in self.classeNameToDevices.items():
            classeItem = QtWidgets.QTreeWidgetItem(self)
            classeItem.setText(0, classeName)
            for device in devices:
                deviceItem = QtWidgets.QTreeWidgetItem(classeItem)
                deviceItem.setText(0, device.name)
                if not device.state:
                    deviceItem.setForeground(0, QtGui.QColor(200, 200, 200))


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = DevicesViewerUI()
    widget.show()
    app.exec_()
