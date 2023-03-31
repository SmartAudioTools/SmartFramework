# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 19:20:45 2021

@author: Baptiste
"""
import pickle
from SmartFramework.serialize import serializePython

leaf_num = 0


class Root:
    def __init__(self):
        print("Root.__init__")
        self.branch1 = Branch()
        self.branch2 = Branch()

    def __reduce__(self):
        return type(self), tuple(), self.__dict__


class Branch:
    def __init__(self):
        print("Branch.__init__")
        self.leaf1 = Leaf()
        self.leaf2 = Leaf()

    def __reduce__(self):
        return type(self), tuple(), self.__dict__


class Leaf:
    def __init__(self):
        print("Leaf.__init__")
        global leaf_num
        leaf_num += 1
        self.value = leaf_num

    def __reduce__(self):
        return type(self), tuple(), self.__dict__


print("construction --------------")
root = Root()
print("----------")
for serializer in [pickle, serializePython]:
    print(serializer.__name__)
    dumped = serializer.dumps(root)
    print(dumped)
    loaded = serializer.loads(dumped)  # ,authorized_classes = [Root,Branch,Leaf])
