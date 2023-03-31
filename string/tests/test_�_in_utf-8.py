# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 10:13:21 2020

@author: Baptiste
"""
e = ord("é".encode("cp1252"))  # ord("é".encode("cp1252"))
strings = []
seconds_alone = set()
seconds = set()
thirds = set()
try:
    l = [e]
    s = bytes(l).decode("utf-8")
    strings.append(s)
except:
    pass
for i in range(128, 192):
    try:
        l = [e, i]
        s = bytes(l).decode("utf-8")
        strings.append(s)
        seconds_alone.add(i)
    except:
        pass
    for j in range(128, 192):
        try:
            l = [e, i, j]
            s = bytes(l).decode("utf-8")
            strings.append(s)
            seconds.add(i)
            thirds.add(j)
        except:
            pass

print("".join(strings))
print(seconds_alone)
print(seconds)
print(thirds)
