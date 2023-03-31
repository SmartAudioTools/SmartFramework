from SmartFramework.files import addToName, changeExt, readLines, writeLines
from SmartFramework.files import dragAndDrop
from googletrans import Translator
from rtf import Rtf

# sys.argv = ["", "C:/Users/Baptiste/powercfg.txt"]
def translateToEnglish(paths):
    translator = Translator(timeout=60)
    for path in paths:
        lines = readLines(path)
        translatedIter = translator.translate(lines, dest="en", src="FR")
        translateds = []
        for translated in translatedIter:
            translateds.append(translated.text)
        newPath = addToName(path, "_En")
        writeLines(newPath, translateds, newline=None)
        newPath = addToName(path, "_Fr_En")
        newPath = changeExt(newPath, "rtf")
        rtf = Rtf(newPath)
        for original, translated in zip(lines, translateds):
            rtf.append(original, "Grey")
            rtf.append(translated, "Black")
        rtf.write()


dragAndDrop(callback=translateToEnglish, group=True, extension="txt")
