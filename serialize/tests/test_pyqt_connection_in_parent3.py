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
from SmartFramework.serialize.serializejson import dumps, loads


class Checkbox(QtWidgets.QCheckBox):
    monSignal = QtCore.Signal([], [bool], [int], [float], [str], [object])


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


app = QtWidgets.QApplication(sys.argv)
widget = QtWidgets.QWidget()
widget.setLayout(QtWidgets.QGridLayout())
app.widget = widget
app.widget.show()
app.exec_()
dumped = dumps(app)
print("dumped ---")
print(dumped)
# del(app)
loaded = loads(dumped, authorized_classes=[QtCore.Qt.WindowFlags, Checkbox])
loaded.widget.show()
loaded.exec_()

print("loaded ---")
loaded_dumped = dumps(loaded)
print(loaded_dumped)
# del(loaded)
assert loaded_dumped == dumped
