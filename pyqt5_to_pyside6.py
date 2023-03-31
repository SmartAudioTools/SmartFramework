#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 16:12:15 2023

@author: smartaudiotools
"""
from SmartFramework.files import searchExt, readLines, write

for path in searchExt("/media/DATA/Python/SmartFace/", "py", recursive=True):
    lines = readLines(path, iterator=False)
    save = False
    for i, line in enumerate(lines):
        if line.find("QtCore.Signal([") != -1 and path != __file__:
            lines[i] = line.replace("[", "(").replace("]", ",)")
            save = True
    if save:
        print(path)
        write(path, lines)
