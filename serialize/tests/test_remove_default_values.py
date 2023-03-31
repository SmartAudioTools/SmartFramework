# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 00:11:54 2021

@author: Baptiste
"""
from SmartFramework.serialize.serializejson import dumps, loads
from SmartFramework.serialize.tools import __getstate__
from SmartFramework.serialize import serialize_parameters


class MaClass:
    def __init__(self):
        self.value_1 = "default_value_1"
        self.value_2 = "default_value_2"

    def __reduce__(self):
        return (
            type(self),
            tuple(),
            __getstate__(self, add=["value_1"], remove_default_values=True),
        )


obj = MaClass()
dumped = dumps(obj)
print(dumped)
loaded = loads(dumped, authorized_classes=[MaClass])
print(loaded.__dict__)
