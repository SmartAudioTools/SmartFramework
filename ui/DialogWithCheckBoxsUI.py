import sys
from qtpy.QtWidgets import QMessageBox, QCheckBox, QVBoxLayout


class DialogWithCheckBoxsUI(QMessageBox):
    def __init__(self, checkboxs, checkStates=None, *args, **argsDict):
        super(DialogWithCheckBoxsUI, self).__init__(*args, **argsDict)
        self.checkboxs = []
        self.setModal(True)
        if checkboxs is not None:
            self.setCheckboxs(checkboxs, checkStates=checkStates)

    def setCheckboxs(self, checkboxs, checkStates=None):
        self.checkboxs = [QCheckBox(text) for text in checkboxs]
        if checkStates is not None:
            for i, checkState in enumerate(checkStates):
                if checkState:
                    self.checkboxs[i].setChecked(True)
        # Access the Layout of the MessageBox to add the Checkbox
        checkBoxsLayout = QVBoxLayout()
        for i, checkbox in enumerate(self.checkboxs):
            checkBoxsLayout.addWidget(checkbox)
        self.layout().addLayout(checkBoxsLayout, 1, 1)

    def exec_(self, *args, **kwargs):
        """
        Override the exec_ method so you can return the value of the checkbox
        """
        return QMessageBox.exec_(self, *args, **kwargs), [
            checkbox.isChecked() for checkbox in self.checkboxs
        ]


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # answer , checkStates = DialogWithCheckBoxsUI( ["Do","not","ask","again"],QMessageBox.Warning,"Dialog with CheckBox","Isn't this checkbox beautiful?",QMessageBox.Cancel |QMessageBox.Ok).exec_()
    answer, checkStates = DialogWithCheckBoxsUI(
        ["participants", "interested", "invited"], [True, True, True]
    ).exec_()

    print(answer == QMessageBox.Ok, checkStates)
