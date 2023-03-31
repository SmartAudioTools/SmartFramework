# -*- coding: utf-8 -*-
"""
Created on Wed May  6 21:22:20 2020

@author: Baptiste
# import time
"""
import sys
from SmartFramework.serialize import (
    serializeRepr,
    serializejson,
    serializePython,
    serializeRepr,
)
import pickle
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.tools.objects import deepCompare
import pickle
from pickle import _dumps

app = QtWidgets.QApplication(sys.argv)
# obj = QtCore.QLocale()

PyQt_pickable =  {
    "QByteArray": QtCore.QByteArray(bytes(range(256))),
    "QColor": QtGui.QColor(10, 20, 30),
    ## "QChar": # n'a plus l'air d'exister dans PyQt5
    "QDate": QtCore.QDate(2020, 10, 31),
    "QDateTime": QtCore.QDateTime(2020, 10, 31, 20, 30,0),
    "QKeySequence": QtGui.QKeySequence(),
    ## "QLatin1Char": # n'a plus l'air d'exister dans PyQt5
    ## "QLatin1String"# n'a plus l'air d'exister dans PyQt5
    "QLine": QtCore.QLine(QtCore.QPoint(0, 1), QtCore.QPoint(2, 3)),
    "QLineF": QtCore.QLineF(QtCore.QPointF(0.0, 1.1), QtCore.QPointF(2.2, 3.3)),
    "QPen": QtGui.QPen(),
    "QBrush": QtGui.QBrush(),
    "QPoint": QtCore.QPoint(0, 1),
    "QPointF": QtCore.QPointF(0.0, 1.1),
    "QPolygon": QtGui.QPolygon([QtCore.QPoint(0, 1), QtCore.QPoint(2, 3)]),
    "QPolygonF": QtGui.QPolygonF(
        [QtCore.QPointF(0.0, 1.1), QtCore.QPointF(2.2, 3.3)]
    ),
    "QRect": QtCore.QRect(QtCore.QPoint(0, 1), QtCore.QPoint(2, 3)),
    "QRectF": QtCore.QRectF(QtCore.QPointF(0.0, 1.1), QtCore.QPointF(2.2, 3.3)),
    "QSize": QtCore.QSize(10, 20),
    "QSizeF": QtCore.QSizeF(10.5, 20.5),
    ## "QMatrix": # Support for the deprecated QMatrix class has been removed
    ## "QString": # n'a plus l'air d'exister dans PyQt5
    "QTime": QtCore.QTime(20, 30),
    "QTransform": QtGui.QTransform(),  # pas reducable dans documentation ?
    "QVector3D": QtGui.QVector3D(),  # pas reducable dans documentation ?
}
for obj_name,obj in PyQt_pickable.items() : 
    serializejson_dumped = pickle.dumps(obj)
    print(serializejson_dumped)
    #print(serializejson_dumped)
    #serializejson_loaded =  serializeRepr_loaded = serializePython.loads(serializejson_dumped)
    #print(deepCompare(obj,serializejson_loaded,return_reason= True))
##obj = C_New_SaveDict_SetState_slots_and_dict()


"""print("serializejson properties , setters getters-----------")

serializejson_dumped = serializejson.dumps(obj,strict_pickle = False,protocol = 4, getters = True, properties = True) #numpy_array_to_list = True
print(serializejson_dumped)
serializejson_loaded = serializejson.loads(serializejson_dumped,authorized_classes = [type(obj)])
print("loaded : ",serializejson_loaded)
print(deepCompare(unpickled,serializejson_loaded,return_reason= True))

print("serializejson -----------")

serializejson_dumped = serializejson.dumps(obj,strict_pickle = False,protocol = 4) #numpy_array_to_list = True
print(serializejson_dumped)
serializejson_loaded = serializejson.loads(serializejson_dumped,authorized_classes = [type(obj)])
print("loaded : ",serializejson_loaded)
print(deepCompare(unpickled,serializejson_loaded,return_reason= True))


print("serializeRepr -----------")
modules = set()

#obj =  complex(1+4j) #numpy.ma.array([1, 2, 3], mask=[0, 1, 0])
# obj = numpy.dtype('int32')
# obj = numpy.int16()
serializeRepr_dumped = serializeRepr.dumps(obj,modules=modules,
    properties = True,
    getters = True,
    setters=True)
print(serializeRepr_dumped)
serializeRepr_loaded = serializeRepr.loads(serializeRepr_dumped,modules=modules)
print("loaded :",serializeRepr_loaded)
print(deepCompare(unpickled,serializeRepr_loaded,return_reason= True))



# loaded = loads(dumped, authorized_classes = QtWidgets.QCheckBox,call_setters=True)
#l#oaded = loads(dumped, authorized_classes = [numpy.ma.core._mareconstruct])  # ,modules=modules

# a = numpyB64("gA==", bool)
# print(a)
# a[2] = True
# print(a)
"""
