# from nltk.corpus import stopwords as stpwords
# from lxml import html
from SmartFramework.files import directory, joinPath
from SmartFramework.serialize.serializejson import load  # ,dump
import os


class languageDetector:
    def __init__(self):
        self.preferedOrder = ["en", "fr", "de", "it", "pt"]
        rootdirectory = directory(__file__) + "/dictionnaires"
        if os.path.exists(rootdirectory):
            fileNames = os.listdir(rootdirectory)
            cleneadlems = dict()
            self._dicos = dict()
            stopwords = {
                key: set(value)
                for key, value in load(
                    joinPath(rootdirectory, "stopwords.json")
                ).items()
            }  # dict()
            for fileN in fileNames:
                if fileN.startswith("lems_"):  # sdevrait utiliser expression regulière
                    langue = fileN[5:7]
                    lemsPath = joinPath(rootdirectory, fileN)
                    lemsDict = load(lemsPath)
                    self._dicos[langue] = set(lemsDict.keys()).union(
                        lemsDict.values()
                    )  # il manque des mot dans keys comme "phonème" !?

    def detect(self, s):
        champs = self.split(s)
        return self.lowerChampslanguageDetect([champ.lower() for champ in champs])

    def split(self, s, spliters="""()[]_-, '"*?.,;:/\|+=<>\t\u2018\u2019&@#§!"""):  #
        for c in spliters:
            s = s.replace(c, "/")
        champs = [x for x in s.split("/") if x != ""]
        return champs

    def lowerChampslanguageDetect(self, champs):
        setChamps = set(champs)
        maxReconnizedWords = -1
        for language, dico in self._dicos.items():
            reconnizedWords = setChamps.intersection(dico)
            lenReconnizedWords = len(reconnizedWords)
            if lenReconnizedWords > maxReconnizedWords:
                maxReconnizedWords = lenReconnizedWords
                bestlanguages = language
            elif lenReconnizedWords == maxReconnizedWords and self.preferedOrder.index(
                language
            ) < self.preferedOrder.index(bestlanguages):
                bestlanguages = language
        return bestlanguages


if __name__ == "__main__":
    print(languageDetect("phonème"))
