# -*- coding: utf-8 -*-
import os.path
import SmartFramework.tools as tools
from SmartFramework.files import write
import os


def loadFile(parFile):
    directory, filename, extension = tools.splitPath(parFile)
    parObject = __import__(filename)
    # os.remove(filename+'.pyc')
    os.popen("attrib +h " + filename + ".pyc")
    return parObject


def saveFile(parObject, parFile="Patch_parametres.py"):
    write(parFile, tools.objectToModuleString(parObject))
