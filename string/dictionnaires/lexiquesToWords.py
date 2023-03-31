# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 19:37:20 2015

@author: Baptiste
"""
from SmartFramework.files import directory, joinPath, readLinesIter
import codecs
import os
from SmartFramework.serialize.serializejson import dump

rootdirectory = directory(__file__)  # + "/dictionnaires"
fileNames = os.listdir(rootdirectory)

for fileName in fileNames:
    if fileName.startswith("lexique_"):  # sdevrait utiliser expression regulière
        langue = fileName[8:10]
        words = []
        dicoPath = joinPath(rootdirectory, fileName)
        for line in readLinesIter(dicoPath, encoding="utf-8"):
            splited = line.replace('"', "").split("\t")
            words.extend(splited[0].split("_"))
        words = sorted(list(set(words)))
        if "" in words:
            words.remove("")
        dump(words, joinPath(rootdirectory, "words_%s.json" % langue))
