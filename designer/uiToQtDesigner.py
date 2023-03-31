# -*- coding: utf-8 -*-
from SmartFramework.designer.uiToPython import uiToPython
from SmartFramework.designer.pythonToQtDesigner import pythonToQtDesigner
from SmartFramework.designer.pywToPy import pywToPy
from SmartFramework.designer.designerParameters import (
    tente_generer_version_non_graphique,
)
from SmartFramework.files import splitPath


def uiToQtDesigner(path):
    pythonPath = uiToPython(path)
    pythonToQtDesigner(pythonPath)
    if tente_generer_version_non_graphique:
        pyPath = pywToPy(pythonPath)
        if pyPath:
            pythonToQtDesigner(pyPath)


if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) > 1:
        path = sys.argv[1]
        directory, filename, extension = splitPath(path)
        try:
            uiToQtDesigner(path)
            os.system("pause")
        except:
            print(sys.exc_info()[1])
            os.system("pause")
    else:
        path = "D:/Projets/Python/SmartFace/patchs/SmartFaceEdit.ui"
        uiToQtDesigner(path)
