# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 11:06:52 2017

@author: Baptiste
"""
import os
import sys
from SmartFramework.files import chercheExt, name
from SmartFramework.designer.pythonToQtDesigner import pythonToQtDesigner

repositories = ["SmartFramework", "SmartFace"]
DIpaths = chercheExt("D:/Projets/Python/SmartFramework/designer/plugins", "py")
pyPaths = []
for repo in repositories:
    pyPaths.extend(
        chercheExt("D:/Projets/Python/" + repo, ["py", "pyw"], recursive=True)
    )
nameToPath = dict()
for pyPath in pyPaths:
    pyName = name(pyPath)
    if pyName in nameToPath:
        if len(pyPath) < len(nameToPath[pyName]):
            nameToPath[pyName] = pyPath
    else:
        nameToPath[pyName] = pyPath
for DIpath in DIpaths:
    fileName = name(DIpath).rstrip("plugin")
    if fileName in nameToPath:
        pyPath = nameToPath[fileName]
        print(pyPath)
        try:
            # print(pyPath)
            pythonToQtDesigner(pyPath)
            # os.system("pause")
        except:
            print(sys.exc_info()[1])
            os.system("pause")
