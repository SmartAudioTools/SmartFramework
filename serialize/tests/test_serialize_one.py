# -*- coding: utf-8 -*-
"""
Created on Wed May  6 21:22:20 2020

@author: Baptiste
# import time
"""
import sys
from SmartFramework.serialize import serializeRepr, serializejson
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.tools.objects import deepCompare
import pickle

app = QtWidgets.QApplication(sys.argv)
# obj = QtWidgets.QPushButton()
##obj = C_New_SaveDict_SetState_slots_and_dict()
obj = QtCore.QByteArray()
print("pickle -----------")

pickled = pickle._dumps(obj)
print(pickled)
unpickled = pickle._loads(pickled)
print("unpickled : ", unpickled)
print(deepCompare(obj, unpickled, return_reason=True))


print("serializejson -----------")
# numpy_array_to_list = True
serializejson_dumped = serializejson.dumps(obj, strict_pickle=True, protocol=3)
print(serializejson_dumped)
serializejson_loaded = serializejson.loads(
    serializejson_dumped, authorized_classes=[type(obj)]
)
print("loaded : ", serializejson_loaded)
print(deepCompare(unpickled, serializejson_loaded, return_reason=True))

print("serializejson properties , setters getters-----------")

serializejson_dumped = serializejson.dumps(
    obj, strict_pickle=False, protocol=4, getters=True, properties=True
)  # numpy_array_to_list = True
print(serializejson_dumped)
serializejson_loaded = serializejson.loads(
    serializejson_dumped, authorized_classes=[type(obj)]
)
print("loaded : ", serializejson_loaded)
print(deepCompare(unpickled, serializejson_loaded, return_reason=True))


print("serializeRepr -----------")
modules = set()

# obj =  complex(1+4j) #numpy.ma.array([1, 2, 3], mask=[0, 1, 0])
# obj = numpy.dtype('int32')
# obj = numpy.int16()
serializeRepr_dumped = serializeRepr.dumps(
    obj, modules=modules, properties=True, getters=True, setters=True
)
print(serializeRepr_dumped)
serializeRepr_loaded = serializeRepr.loads(serializeRepr_dumped, modules=modules)
print("loaded :", serializeRepr_loaded)
print(deepCompare(unpickled, serializeRepr_loaded, return_reason=True))


# loaded = loads(dumped, authorized_classes = QtWidgets.QCheckBox,call_setters=True)
# l#oaded = loads(dumped, authorized_classes = [numpy.ma.core._mareconstruct])  # ,modules=modules

# a = numpyB64("gA==", bool)
# print(a)
# a[2] = True
# print(a)
