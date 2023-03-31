from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.save.save import Save
from SmartFramework.save.collInterface import CollInterface
from SmartFramework.ui.numberUI import NumberUI


class AudioPreferencesUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AudioPreferencesUI, self).__init__(parent)
        self.resize(222, 125)
        self.groupBox_2 = QtWidgets.QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(0, 0, 221, 121))
        self.save_3 = Save(self.groupBox_2, saveName="val3", collName="audioParameters")
        self.numberui = NumberUI(self.groupBox_2)
        self.numberui.setGeometry(QtCore.QRect(20, 20, 50, 22))
        self.numberui_2 = NumberUI(self.groupBox_2)
        self.numberui_2.setGeometry(QtCore.QRect(20, 50, 50, 22))
        self.save_2 = Save(self.groupBox_2, saveName="val2", collName="audioParameters")
        self.save = Save(self.groupBox_2, saveName="val1", collName="audioParameters")
        self.numberui_3 = NumberUI(self.groupBox_2)
        self.numberui_3.setGeometry(QtCore.QRect(20, 80, 50, 22))
        self.collinterface = CollInterface(
            self.groupBox_2, collName="audioParameters", fileName="audioParameters"
        )

        self.save_3.output["int"].connect(self.numberui_3.input)
        self.save_2.output["int"].connect(self.numberui_2.input)
        self.save.output["int"].connect(self.numberui.input)
        self.numberui_3.output["int"].connect(self.save_3.input)
        self.numberui_2.output["int"].connect(self.save_2.input)
        self.numberui.output["int"].connect(self.save.input)

        self.groupBox_2.setTitle(
            QtWidgets.QApplication.translate(
                "self", "GroupBox", None, QtWidgets.QApplication.UnicodeUTF8
            )
        )

    @QtCore.Slot(str)
    def input(self, obj):
        self.collinterface.saveAndLoad(obj)

    def sizeHint(self):
        return self.size()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = AudioPreferencesUI()
    widget.show()
    sys.exit(app.exec_())
