# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 19:37:20 2015

@author: Baptiste
"""
from SmartFramework.files import directory, joinPath, readLinesIter
import os
from SmartFramework.serialize.serializejson import dump

rootdirectory = directory(__file__)  # + "/dictionnaires"
fileNames = os.listdir(rootdirectory)
chars = dict()
for fileName_ in fileNames:
    if fileName_.startswith("lexique_"):  # sdevrait utiliser expression regulière

        dico = dict()
        langue = fileName_[8:10]
        dicoPath = joinPath(rootdirectory, fileName_)
        chars_langue = set()
        for line in readLinesIter(dicoPath, encoding="utf-8"):
            splited = line.replace('"', "").split("\t")
            word = splited[1]
            dico[splited[0]] = word
            chars_langue.update(word)
        chars[langue] = "".join(sorted(chars_langue))
        dump(dico, joinPath(rootdirectory, "lems_%s.json" % langue))
# pourquoi il ne veut pas serializer?
dump(chars, joinPath(rootdirectory, "chars.json" % langue))
