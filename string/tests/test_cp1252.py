# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 17:38:51 2020

@author: Baptiste
"""
not_valids = []
valids = []
for i in range(255):
    try:
        bytes([i]).decode("cp1252")
        valids.append(i)
    except:
        not_valids.append(i)
print(not_valids)

for valid in valids:
    string = bytes([valid]).decode("cp1252")
    bytesUtf8 = string.encode("utf-8")
    try:
        bytesUtf8.decode("cp1252")
    except:
        print(string)
