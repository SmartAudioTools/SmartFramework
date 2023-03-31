# import rapidjson
# from collections import deque
# from SmartFramework.tools.objects import (
##    class_str_from_class,
#   instance,
#   from_name,
# )  # ,from_id


# not_duplicates_types = set([type(None), bool, int, float, str])

# from __main__ import Root,Branch,Leaf
import sys
from qtpy import QtWidgets, QtCore
from collections import defaultdict
from SmartFramework.serialize.serializePython import dumps, loads

# from SmartFramework.serialize.serializeRepr import dumps , loads


class Checkbox(QtWidgets.QCheckBox):
    monSignal = QtCore.Signal([], [bool], [int], [float], [str], [object])


app = QtWidgets.QApplication(sys.argv)


def exemple_1():
    widget = QtWidgets.QWidget()
    widget.checkbox1 = QtWidgets.QCheckBox(parent=widget)
    widget.checkbox2 = QtWidgets.QCheckBox(parent=widget)
    widget.checkbox2.setGeometry(0, 20, 20, 20)
    widget.checkbox1.stateChanged[int].connect(widget.checkbox2.setCheckState)
    widget.show()
    return widget


def exemple_2():
    checkbox1 = QtWidgets.QCheckBox()
    checkbox2 = QtWidgets.QCheckBox()
    checkbox1.stateChanged[int].connect(checkbox2.setCheckState)
    checkbox1.show()
    checkbox2.show()
    checkboxs = [checkbox1, checkbox2]
    return checkboxs


def exemple_3():
    widget = QtWidgets.QWidget()
    widget.checkbox1 = Checkbox(parent=widget)
    widget.checkbox2 = QtWidgets.QCheckBox(parent=widget)
    widget.checkbox2.setGeometry(0, 20, 20, 20)
    widget.checkbox1.monSignal.connect(widget.checkbox2.setCheckState)
    widget.checkbox1.monSignal[bool].connect(widget.checkbox2.setCheckState)
    widget.checkbox1.monSignal[int].connect(widget.checkbox2.setCheckState)
    widget.checkbox1.monSignal[float].connect(widget.checkbox2.setCheckState)
    widget.checkbox1.monSignal[str].connect(widget.checkbox2.setCheckState)
    widget.checkbox1.monSignal[object].connect(widget.checkbox2.setCheckState)
    widget.show()
    return widget


obj = exemple_1()

app.exec_()


print("dumped ---")
dumped = dumps(obj)
print(dumped)

print("loaded ---")
# authorized_classes = [QtCore.Qt.WindowFlags,Connection,Checkbox])
loaded = loads(dumped)
print(dumps(loaded))

try:
    loaded.show()
except:
    pass
app.exec_()
