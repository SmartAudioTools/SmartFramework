# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 18:39:53 2020

@author: Baptiste
"""

chars = "àáâãäåæçèéêëìíî€©µ"
print("utf-8-> bytes -> cp1252")
for c in chars:
    try:
        out = c.encode("utf-8").decode("cp1252")
        print(c, "->", out)
    except:
        print(c, "-> ERROR")


print("cp1252 -> bytes -> utf-8")
for c in chars:
    try:
        out = c.encode("cp1252").decode("utf-8")
        print(c, "->", out)
    except:
        print(c, "-> ERROR")
