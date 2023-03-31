# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:02:48 2020

@author: Baptiste
"""

print("Ecriture-------\n")

string = "salut bidule !\n comment ça va?"
for newline in [None, "", "\n", "\r", "\r\n"]:
    with open("test_newline.txt", "w", newline=newline) as f:
        f.writelines([string])
    with open("test_newline.txt", "rb") as f:
        print(repr(newline), f.read())


print("read -------\n")
b = b"Salut bidule !\ncomment ca va?\rIl fait beau chez toi ?\r\nOu c'est la merde?"
with open("test_newline.txt", "wb") as f:
    f.write(b)
for newline in [None, "", "\n", "\r", "\r\n"]:
    with open("test_newline.txt", "r", newline=newline) as f:
        print(repr(newline), ":")
        print(repr(f.read()))

print("readline -------\n")
for newline in [None, "", "\n", "\r", "\r\n"]:
    with open("test_newline.txt", "r", newline=newline) as f:
        print(repr(newline), ":")
        print(repr(f.readline()))


print("readlines -------\n")
for newline in [None, "", "\n", "\r", "\r\n"]:
    with open("test_newline.txt", "r", newline=newline) as f:
        print(repr(newline), ":")
        print(repr(f.readlines()))
