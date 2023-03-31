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
from qtpy import QtWidgets, QtGui, QtCore
from collections import defaultdict
from SmartFramework.serialize import serializejson as serializejson
from parse import parse


import ctypes


def object_from_id(_id):
    return ctypes.cast(_id, ctypes.py_object).value


# SERIALISATION DES CONNECTIONS -----------------------------------------------

# hack pour enregistrer les connextions
old_connect = QtCore.pyqtBoundSignal.connect
# connections = defaultdict(list)
connections_counter = 0


def new_connect(signal, slot):
    # connections[signal].append(slot)
    global connections_counter
    connections_counter += 1
    old_connect(signal, slot)
    signal_object, signal_name, signature, slot_object, slot_name = connection_infos(
        signal, slot
    )
    if "~signals" not in signal_object.__dict__:
        signal_object.__dict__["~signals"] = []
    signal_object.__dict__["~signals"].append(
        connection(connections_counter, signal_name, signature)
    )
    if "~slots" not in slot_object.__dict__:
        slot_object.__dict__["~slots"] = []
    slot_object.__dict__["~slots"].append(
        connection(connections_counter, slot=slot_name)
    )


QtCore.pyqtBoundSignal.connect = new_connect


class connection:
    def __init__(self, id, signal=None, signature=None, slot=None):
        self.id = id
        if signal is not None:
            self.signal = signal
        if signature is not None:
            self.signature = signature
        if slot is not None:
            self.slot = slot


# old_disconnect = QtCore.pyqtBoundSignal.disconnect
# def disconnect(signal):
##    connections.pop(signal)
#    old_disconnect(signal)
# QtCore.pyqtBoundSignal.disconnect = disconnect

signature_str_from_qt = {
    "": None,
    "bool": "bool",
    "int": "int",
    "double": "float",
    "QString": "str",
    "PyQt_PyObject": "object",
}
stignature_from_srt = {
    "bool": bool,
    "int": int,
    "float": float,
    "str": str,
    "object": object,
}


def connection_infos(signal, slot):
    signal_str = signal.__str__()
    signal_name, class_name, hex_id = parse(
        "<bound PYQT_SIGNAL {} of {} object at {}>", signal_str
    ).fixed
    signal_object = object_from_id(int(hex_id, 16))
    signal_str = signal.signal
    signature = signature_str_from_qt[signal_str[signal_str.rfind("(") + 1 : -1]]
    slot_object = slot.__self__
    slot_name = slot.__name__
    return (signal_object, signal_name, signature, slot_object, slot_name)


class Connection:
    def __init__(self, obj_1, signal_name, signature, obj_2, slot_name, make=True):
        self.obj_1 = obj_1
        self.signal = signal_name
        if signature is not None:
            self.signature = signature
        self.obj_2 = obj_2
        self.slot = slot_name

    def __setstate__(self, state):
        signal = getattr(state["obj_1"], state["signal"])
        if "signature" in state:
            signal = signal.__getitem__(stignature_from_srt[state["signature"]])
        signal.connect(getattr(state["obj_2"], state["slot"]))


def record_connections_in_parent():
    for methode, slots in connections.items():
        signal_name, class_name, hex_id = parse(
            "<bound PYQT_SIGNAL {} of {} object at {}>", methode.__str__()
        ).fixed
        signal_str = methode.signal
        signature = signature_str_from_qt[signal_str[signal_str.rfind("(") + 1 : -1]]
        print(str(signature))
        # signature = signature_from_str[signature_str]
        obj_1 = object_from_id(int(hex_id, 16))
        for slot in slots:
            obj_2 = slot.__self__
            parents_1 = get_parents(obj_1)
            parents_2 = get_parents(obj_2)
            for parent in parents_1:
                if parent in parents_2:
                    break
            else:
                raise
            # print(parent , obj_1,signal_name,"->",obj_2,slot.__name__)
            if "~connections" not in parent.__dict__:
                parent.__dict__["~connections"] = []
            parent.__dict__["~connections"].append(
                Connection(obj_1, signal_name, signature, obj_2, slot.__name__)
            )

        # recherche ancètres


def get_parents(obj):
    parent = obj.parent()
    parents = []
    while parent is not None:
        parents.append(parent)
        parent = parent.parent()
    return parents


# -----------------------------------------------------------------------------


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


obj = exemple_3()

app.exec_()


print("dumped ---")
# encoder = Encoder(indent="\t", sort_keys=True, ensure_ascii=False)
# record_connections_in_parent()
dumped = serializejson.dumps(obj)
print(dumped)

print("loaded ---")
loaded = serializejson.loads(
    dumped, authorized_classes=[QtCore.Qt.WindowFlags, Connection, Checkbox]
)
print(serializejson.dumps(loaded))

try:
    loaded.show()
except:
    pass
app.exec_()
