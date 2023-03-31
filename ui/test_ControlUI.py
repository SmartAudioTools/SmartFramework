import sys
from qtpy import QtWidgets
from SmartFramework.ui.ControlUI import ControlUI

app = QtWidgets.QApplication(sys.argv)


# items={"none": 0, "selected": 1, "all": 2}

controlUI = ControlUI(decimals=1, displayMinimum=-15, displayMaximum=229, suffix="dB")
# controlUI = ControlUI(maximum=127., decimals=1)
controlUI.show()
app.exec_()
