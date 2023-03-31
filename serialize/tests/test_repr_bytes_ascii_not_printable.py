# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 16:01:50 2021

@author: Baptiste
"""

from SmartFramework.serialize.serializeRepr import dumps

bytes_ = bytes(range(100))
# bytes_ = b"oiu"
dumped = dumps("teraz")
print(dumped)
