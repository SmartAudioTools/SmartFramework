# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets


class CenteredComboBoxUI(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        # les initArgs sont utiles pour avoir des valeure par defaut
        QtWidgets.QComboBox.__init__(self, parent)
        # self.timer =
        self.setEditable(True)
        self._lineEdit = self.lineEdit()
        self._lineEdit.setReadOnly(True)
        self._lineEdit.setAlignment(QtCore.Qt.AlignHCenter)
        # permet ouverture popup quand clique sur widget      :
        self._lineEdit.installEventFilter(self)
        self.setStyleSheet("QWidget{text-align: right}")  # ne marche pas

        # self.setStyleSheet("""QComboBox::drop-down {background: black;max-width: 1px;}""")

    def eventFilter(self, obj, event):
        """Function to filter out the unwanted events and add new functionalities for it."""
        eventType = event.type()
        if obj == self._lineEdit:
            if eventType == QtCore.QEvent.MouseButtonDblClick:
                # empeche la selection de text dans lineedit par double click:
                return True
            if eventType == QtCore.QEvent.MouseButtonPress:
                self.showPopup()
        return False


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = CenteredComboBoxUI()
    widget.addItems(["oui", "non"])
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
