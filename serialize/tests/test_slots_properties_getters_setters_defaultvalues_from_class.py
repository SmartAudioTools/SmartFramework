import sys
from qtpy import QtWidgets, QtCore, QtGui

app = QtWidgets.QApplication(sys.argv)
from objects import pyqt_objects
from pickle import _dumps
from SmartFramework.serialize import serializejson

# from SmartFramework.serialize.tests.objects.pyqt_objects import objects
from SmartFramework.serialize.tools import (
    slots_properties_getters_setters_from_class,
    __getstate__,
)


class MyClass:
    def __init__(self):
        pass

    def setx(self, x):
        self._x = x

    def getx(self):
        return self._x

    x = property(getx, setx)


log = print


class C_slots_properties_getters_setters(QtCore.QObject):
    # sert a pouvoir executer code spécifique a la restauration

    __slots__ = ("a", "c")

    def __init__(self, a="a", b="b", c="c", d="d", e="e", f="f", g="g", h="h", i="i"):
        QtCore.QObject.__init__(self)
        log(f"        __init__({a},{b},{c},{d},{e},{f},{g},{h},{i})")
        self.__dict__["i"] = i
        self.__dict__["h"] = h
        self.__dict__["g"] = g
        self.__dict__["f"] = f
        self.__dict__["e"] = e
        self.d = d
        self.c = c
        self.b = b
        self.a = a

    def __setstate__(self, state):
        self.__dict__.update(state)
        log("        __setstate__(" + repr(state) + ")")

    def setb(self, value):
        log("seta() called")
        self.b = value

    def set_c(self, value):
        log("setb() called")
        self.c = value

    def setD(self, value):
        log("setc() called")
        self.d = value

    @property  # @pyqtProperty(int) en pyqt
    def e(self):
        return self.__dict__["e"]

    @e.setter  # idem en pyqt
    def e(self, value):
        log("e setter called")
        self.__dict__["e"] = value

    def getf(self):
        return self.__dict__["f"]

    def setf(self, value):
        log("f setter called")
        self.__dict__["f"] = value

    f = property(getf, setf)

    def getg(self):
        return self.__dict__["g"]

    def setg(self, value):
        log("g setter called")
        self.__dict__["g"] = value

    @QtCore.Property(str)
    def h(self):
        return self.__dict__["h"]

    @h.setter  # idem en pyqt
    def h(self, value):
        print("h setter called")
        self.__dict__["h"] = value

    def geti(self):
        return self.__dict__["i"]

    def seti(self, value):
        print("i setter called")
        self.__dict__["i"] = value

    i = QtCore.Property(str, geti, seti)


# obj =    QtGui.QImage("")
# clsses
classes = C_slots_properties_getters_setters, QtCore.QTime
for class_ in classes:
    print(class_.__name__, "---------------")
    obj = class_()
    # obj.a = 'oui'
    print(slots_properties_getters_setters_from_class(class_))
#    #print()
#    print(__getstate__(obj,split_dict_slots = True,properties = True,getters = True, remove_default_values = False))
#
#    print(serializejson.dumps(obj))
##for categorie, objects in pyqt_objects.objects.items() :
#    for name,obj in objects.items() :
#        print (name)
#        print (slots_properties_getters_setters_from_class(type(obj)))
# obj = MyClass()
# obj2= pickle.loads(pickle.dumps(obj))
