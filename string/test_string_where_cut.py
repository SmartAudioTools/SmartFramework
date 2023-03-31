# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 13:52:56 2020

@author: Baptiste
"""

from SmartFramework.string import not_8bit_common_encodings

for encoding in not_8bit_common_encodings:
    print(encoding, ":", repr("\n".encode(encoding)))
