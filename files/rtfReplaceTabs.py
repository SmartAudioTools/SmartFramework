# -*- coding: utf-8 -*-
def pardToString(pardDict):
    champs = []
    for key, value in pardDict.iteritems():
        if value is not None:
            champ = key + str(value)
        else:
            champ = key
        champs.append(champ)
    return "\\pard" + "".join(["\\" + champ for champ in champs])


def pardParse(line):
    ##print '--------------'
    # print(line)
    pardStart = line.find("\\pard")
    parseStart = pardStart
    tabs = 0
    pardDict = None
    text = bool(
        line.find(" ") != -1
    )  # test un peu grossier , peut considerer à tord que y'a du text

    if parseStart == -1:
        if len(line) > 2 and line[0] == "\\" and line[1] != "\\":
            firstTab = line.find("\\tab")
            firstSpace = line.find(" ")
            if firstTab < firstSpace or firstSpace == -1:
                parseStart = firstTab

    if parseStart != -1:
        parseEnd = line.find(" ", parseStart)

        if parseEnd == -1:
            parseEnd = len(line)
            text = False

        crochetAfterSart = line.find("{", parseStart)
        if crochetAfterSart != -1 and crochetAfterSart < parseEnd:
            parseEnd = crochetAfterSart

        if pardStart != -1:
            pardDict = dict()
        # print(parseStart,parseEnd)
        pardLine = line[parseStart:parseEnd]
        # print(pardLine)
        champs = pardLine.split("\\")[1:]
        # print(champs)
        cleanedChamps = []
        for champ in champs:
            if champ == "tab":
                tabs += 1
            else:
                for index, c in enumerate(champ):
                    if (c.isdigit() and champ[index:].isdigit()) or (
                        c == "-" and champ[index + 1 :].isdigit()
                    ):
                        key = champ[:index]
                        value = int(champ[index:])
                        break
                else:
                    key = champ
                    value = None
                if key in ["sa", "sl", "slmult", "pard", "li", "fi", "qc", "qr", "qj"]:
                    if key != "pard":
                        pardDict[key] = value
                else:
                    cleanedChamps.append(champ)
        if pardDict is not None:
            if "li" not in pardDict:
                pardDict["li"] = 0
            if "fi" not in pardDict:
                pardDict["fi"] = 0
        cleanedLine = (
            line[:parseStart]
            + "".join(["\\" + champ for champ in cleanedChamps])
            + line[parseEnd:]
        )
        return pardDict, tabs, cleanedLine, parseStart, text
    else:
        return None, 0, line, 0, text


try:
    import sys
    import os
    from SmartFramework.files import cleanDropNames, directory, name, chercheExt, ext

    os.chdir(directory(__file__))
    cleanDropNames(sys.argv)
    jsonPaths = [path for path in sys.argv[1:] if ext(path) == "json"]
    directories = [path for path in sys.argv[1:] if os.path.isdir(path)]
    rtfPaths = [path for path in sys.argv[1:] if ext(path) == "rtf"]
    # rtfPaths = ["test1.rtf"]
    for directorie in directories:
        rtfPaths.extend(chercheExt(directorie, "rtf", recursive=True))
    for rtfPath in rtfPaths:
        print(name(rtfPath))
        rtfFile = open(rtfPath, "rb")
        rtfLines = rtfFile.read().splitlines()
        rtfFile.close()
        # actualInPard = None
        actualInPard = {"li": 0, "fi": 0}
        actualOutPard = {"li": 0, "fi": 0}
        wantedPard = {"li": 0, "fi": 0}  # None
        # lastPard = None
        for lineNumber, line in enumerate(rtfLines):
            # print(line)
            pard, nbTabs, cleanedLine, pardStart, text = pardParse(line)
            # print(pard,nbTabs ,pardStart,text)
            # print(cleanedLine)
            if pard is not None:
                actualInPard = pard
                wantedPard = actualInPard.copy()
            # if wantedPard is not None :
            if text:
                if actualInPard.get("fi", 0):
                    wantedPard["li"] = actualInPard["li"]
                    wantedPard["fi"] = actualInPard["fi"] + nbTabs * 720
                else:
                    wantedPard["li"] = actualInPard["li"] + nbTabs * 720
                    wantedPard["fi"] = 0
                    # if "fi" in wantedPard :
                    #    del(wantedPard["fi"])
            else:
                wantedPard["li"] = actualOutPard["li"]
                if "fi" in actualOutPard:
                    wantedPard["fi"] = actualOutPard["fi"]
                elif "fi" in wantedPard:
                    del wantedPard["fi"]

            # suprime les premier tab avant text ()
            if nbTabs:
                rtfLines[lineNumber] = cleanedLine.strip()

            # ajoute , suprime ou modifie la definition d'un paragraphe
            if wantedPard != actualInPard or wantedPard != actualOutPard:
                if wantedPard != actualOutPard:
                    if (
                        pardStart != 0
                        or cleanedLine[pardStart] == " "
                        or (cleanedLine[pardStart] == "\\")
                    ):
                        space = ""
                    else:
                        space = " "
                    newLine = (
                        cleanedLine[:pardStart]
                        + pardToString(wantedPard)
                        + space
                        + cleanedLine[pardStart:]
                    )
                    rtfLines[lineNumber] = newLine.strip()
                    actualOutPard = wantedPard.copy()
                else:
                    rtfLines[lineNumber] = cleanedLine.strip()

            """    
            elif pard is not None  # actualInPard = pard
                if lastPard == actualPard
                    # suprime la definition d'un paragraphe:
                    rtfLines[lineNumber] = cleanedLine.strip() 
                else : 
                    actualPard["li"] = wantedLi
                    newLine = cleanedLine[:pardStart]   +  pardToString(actualPard)  +  cleanedLine[pardStart:]           
                    rtfLines[lineNumber] = newLine.strip()
                    lastLi = wantedLi                   
               """

            # print(rtfLines[lineNumber])

        rtfOutFile = open(rtfPath, "wb")
        # rtfOutFile = open(addToName(rtfPath,"_out"),"wb")
        rtfOutFile.write("\r\n".join(rtfLines))
        rtfOutFile.close()

    os.system("pause")


except:
    import traceback

    # print("erreure avec le fichier : %s" % jsonPath)
    traceback.print_exc()
    os.system("pause")
