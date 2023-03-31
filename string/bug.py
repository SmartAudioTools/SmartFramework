import os
from simplejson import loads


def load(f, default=None, **argsDict):
    f = open(f, "rb")  # avec 'r' il ne sais pas lire les accents dans les fichier json
    string = (
        f.read()
    )  # ne sert à rien de faire simplejson.load(f) en esperant utiliser moins de memoire car en interne il fait un f.read()
    f.close()
    return loads(string, **argsDict)


rootdirectory = os.path.dirname(__file__).replace("\\", "/") + "/dictionnaires"
if os.path.exists(rootdirectory):
    fileNames = os.listdir(rootdirectory)
    cleneadlems = dict()
    dicos = dict()
    stopwords = {
        key: set(value)
        for key, value in load(rootdirectory + "/stopwords.json").items()
    }
    for fileN in fileNames:
        if fileN.startswith("lems_"):  # sdevrait utiliser expression regulière
            langue = fileN[5:7]
            lemsPath = rootdirectory + "/" + fileN
            lemsDict = load(lemsPath)
            dicos[langue] = set(lemsDict.keys()).union(
                lemsDict.values()
            )  # il manque des mot dans keys comme "phonème" !?
import cv2
import skimage
import ctypes

dll_name = "D:/Projets/Python/SmartFramework/video/devices/CLEyeMulticam.dll"
ctypes.cdll.LoadLibrary(str(dll_name))
