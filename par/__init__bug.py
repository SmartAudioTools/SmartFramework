# -*- coding: utf-8 -*-
import pickle
import os.path


def splitFileName(path):
    realpath = os.path.realpath(path)
    repertoirScript = os.path.dirname(realpath)
    directory, file = os.path.split(realpath)
    filename, extension = os.path.splitext(file)
    extension = extension[1:]
    return directory, filename, extension


def jointFileName(directory, filname, extension):
    return os.path.join(directory, filname) + "." + extension


def findParFile(path):
    directory, filename, extension = splitFileName(path)

    # cherche fichier Par en regardant d'abord nom du script, puis nom sans sub-version , puis nom sans version
    versions = filename.split("_")
    for i in range(len(versions), 0, -1):
        parFile = jointFileName(directory, "_".join(versions[:i]), "par")
        if os.path.exists(parFile):
            return parFile
    # cherche fichier Parametres.par
    parFile = jointFileName(directory, "Parametres", "par")
    if os.path.exists(parFile):
        return parFile


def loadParFile(parFile):
    parFileP = open(parFile, "r")
    parObject = pickle.load(parFileP)
    parFileP.close()
    return parObject


def saveParFile(parObject, parFile="parametres.par"):
    parFileP = open(parFile, "w")
    pickle.dump(parObject, parFileP)
    parFileP.close()


def objToPyClass(obj, indentation=0):
    stringAll = ""
    maclasse = str(obj.__class__)
    maclasse = maclasse[maclasse.rfind(".") + 1 :]
    stringAll = stringAll + "    " * indentation + "class " + maclasse + "():" + "\n"
    attribut_dictionnaire = obj.__dict__
    for attributName in attribut_dictionnaire.keys():
        attributVal = attribut_dictionnaire[attributName]
        if type(attributVal) == str:
            attributestring = "'" + str(attribut_dictionnaire[attributName]) + "'"
        elif str(type(a)) == "<type 'instance'>":
            attributestring = objToPyClass
        else:
            attributestring = str(attribut_dictionnaire[attributName])
        stringAll = stringAll + "    " + attributName + " = " + attributestring + "\n"
    return stringAll
