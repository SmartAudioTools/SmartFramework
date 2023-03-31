# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 15:22:04 2021

@author: Baptiste
"""

import ctypes
import sys


class Truc:
    pass


a = {"coucou": 4}
b = Truc()
mutate(a, b)
print(a)
