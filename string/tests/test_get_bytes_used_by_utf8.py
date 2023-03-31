# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 15:33:58 2020

@author: Baptiste
"""
valide_1_byte = []
not_valide_1_byte = []
for byte1 in range(256):
    bytes_ = bytes([byte1])
    try:
        bytes_.decode("utf-8")
        valide_1_byte.append(byte1)
    except:
        not_valide_1_byte.append(byte1)

print(valide_1_byte)
print(not_valide_1_byte)
