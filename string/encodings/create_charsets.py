# -*- coding: utf-8 -*-
"""
Created on Fri May  1 19:17:16 2020

@author: Baptiste
"""

bytes_ = bytes(range(256))

from dictionnaires import dicos

dicos["fr"]

rootdirectory = directory(__file__)  # + "/dictionnaires"
fileNames = os.listdir(rootdirectory + "/dictionnaires")
lems = dict()
for fileName_ in fileNames:
    if fileName_.startswith("lexique_"):  # sdevrait utiliser expression regulière
        langue = fileName_[8:10]
        dicoPath = joinPath(rootdirectory, fileName_)
        dico = dict()
        chars = set()
        for line in readLinesIter(dicoPath, encoding="utf-8"):
            splited = line.replace('"', "").split("\t")
            dico[splited[0]] = splited[1]
        lems[langue] = dico
        dump(lems[langue], joinPath(rootdirectory, "lems_%s.json" % langue))
