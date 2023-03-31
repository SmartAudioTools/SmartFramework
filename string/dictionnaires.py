from SmartFramework.files import directory, joinPath
from SmartFramework.serialize.serializejson import load  # ,dump
import os

# from SmartTime.languageAbreviations import abreviationToLanguage

rootdirectory = directory(__file__) + "/dictionnaires"
if os.path.exists(rootdirectory):
    fileNames = os.listdir(rootdirectory)
    cleneadlems = dict()
    dicos = dict()
    stopwords = {
        key: set(value)
        for key, value in load(joinPath(rootdirectory, "stopwords.json")).items()
    }
    for fileN in fileNames:
        if fileN.startswith("lems_"):  # devrait utiliser expression regulière
            langue = fileN[5:7]
            lemsPath = joinPath(rootdirectory, fileN)
            lemsDict = load(lemsPath)
            dicos[langue] = set(lemsDict.keys())
            lems = set(lemsDict.values())
            cleneadlems[langue] = {
                key: value for key, value in lemsDict.items() if key not in lems
            }
            # stopwords[langue] = stpwords.words(abreviationToLanguage[langue])# set()
    # dump(stopwords,)
