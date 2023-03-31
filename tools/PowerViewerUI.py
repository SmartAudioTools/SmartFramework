from qtpy import QtGui, QtWidgets
from qtpy.QtCore import Qt
from SmartFramework.tools.power import Query


class PowerViewerUI(QtWidgets.QTreeWidget):
    def __init__(self, parent=None, sortingEnabled=True):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.setColumnCount(3)
        self.setHeaderLabels(["Parametre", "Secteur", "Batterie"])
        # self.header().close()
        for subGroup, parameters in Query().items():
            subGroupItem = QtWidgets.QTreeWidgetItem(self)
            subGroupItem.setText(0, subGroup)
            for parameter in parameters:
                parameterItem = QtWidgets.QTreeWidgetItem(subGroupItem)
                parameterItem.setText(0, parameter.name)
                if parameter.indexToName:
                    parameterItem.setText(1, parameter.indexToName[parameter.acIndex])
                    parameterItem.setText(2, parameter.indexToName[parameter.dcIndex])
                else:
                    parameterItem.setText(
                        1, "{} {}".format(parameter.acIndex, parameter.unit)
                    )
                    parameterItem.setText(
                        2, "{} {}".format(parameter.dcIndex, parameter.unit)
                    )

        self.sortByColumn(0, Qt.AscendingOrder)


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = PowerViewerUI()
    widget.show()
    app.exec_()
