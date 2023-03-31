# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 15:24:40 2018

@author: Baptiste
"""
import subprocess
import parse

info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = subprocess.SW_HIDE


def getActiveNameAndGUID():
    string = (
        subprocess.Popen(
            ["powercfg", "-GETACTIVESCHEME"], stdout=subprocess.PIPE, startupinfo=info
        )
        .communicate()[0]
        .decode("cp850")
    )
    parsedDict = parse.parse("{}: {GUID}  ({NAME})", string).named
    return parsedDict["NAME"], parsedDict["GUID"]


def getActive():
    string = (
        subprocess.Popen(
            ["powercfg", "-GETACTIVESCHEME"], stdout=subprocess.PIPE, startupinfo=info
        )
        .communicate()[0]
        .decode("cp850")
    )
    return parse.parse("{}: {}  ({})", string)[2]


def setActive(NameOrGUID):
    nameToGUID = getNameToGUID()
    if NameOrGUID in nameToGUID:
        subprocess.call(["powercfg", "-SETACTIVE", nameToGUID[NameOrGUID]])
    else:
        subprocess.call(["powercfg", "-SETACTIVE", NameOrGUID])
    # return GUID


def getNameToGUID():
    string = (
        subprocess.Popen(
            ["powercfg", "-LIST"], stdout=subprocess.PIPE, startupinfo=info
        )
        .communicate()[0]
        .decode("cp850")
    )
    nameToGUID = dict()
    for line in string.splitlines():
        parsed = parse.parse("{}: {GUID}  ({NAME})", line)
        if not parsed:
            parsed = parse.parse("{}: {GUID}  ({NAME}){CURENT}", line)
        if parsed:
            parsedDict = parsed.named
            nameToGUID[parsedDict["NAME"]] = parsedDict["GUID"]
    return nameToGUID


class Parameter:
    def __init__(
        self,
        name,
        GUID,
        acIndex,
        dcIndex,
        indexToName=None,
        minValue=None,
        maxValue=None,
        inc=None,
        unit=None,
    ):
        self.__dict__.update(locals())


def Query():
    string = (
        subprocess.Popen(
            ["powercfg", "-QUERY"], stdout=subprocess.PIPE, startupinfo=info
        )
        .communicate()[0]
        .decode("cp850")
        .replace("\xa0", " ")
    )
    lines = string.splitlines()
    IDtoName = dict()
    i = 1
    subGroupParameters = {}
    if lines[i].startswith("  Alias de GUID : "):
        i += 1
    while i < len(lines):
        name = None
        GUID = None
        indexToName = {}
        minValue = None
        maxValue = None
        inc = None
        unit = None
        acIndex = None
        dcIndex = None
        while lines[i].startswith("  GUID du sous-groupe"):
            subGroupGUID, subGroupName = parse.parse(
                "  GUID du sous-groupe : {}  ({})", lines[i]
            )
            IDtoName[subGroupGUID] = subGroupName
            i += 1
        if lines[i].startswith("    Alias de GUID : "):
            i += 1
        GUID, name = parse.parse(
            "    GUID du paramètre d'alimentation : {}  ({})", lines[i]
        )
        IDtoName[GUID] = name
        i += 1
        if lines[i].startswith("      Alias de GUID : "):
            i += 1
        while lines[i].startswith("      Index possible"):
            parameterIndex = int(
                parse.parse("      Index possible du paramètre : {}", lines[i])[0]
            )
            i += 1
            parametreIndexName = parse.parse(
                "      Nom convivial possible du paramètre : {}", lines[i]
            )[0]
            indexToName[parameterIndex] = parametreIndexName
            i += 1
        if lines[i].startswith("      Valeur minimale possible"):
            minValue = int(
                parse.parse("      Valeur minimale possible : {}", lines[i])[0], 0
            )
            i += 1
            maxValue = int(
                parse.parse("      Valeur maximale possible : {}", lines[i])[0], 0
            )
            i += 1
            inc = int(
                parse.parse("      Incrément possible des paramètres : {}", lines[i])[
                    0
                ],
                0,
            )
            i += 1
            unit = parse.parse("      Unités possibles des paramètres : {}", lines[i])[
                0
            ]
            i += 1
        acIndex = int(
            parse.parse(
                "    Index actuel du paramètre de courant alternatif : {}", lines[i]
            )[0],
            0,
        )
        i += 1
        dcIndex = int(
            parse.parse(
                "    Index actuel du paramètre de courant continu : {}", lines[i]
            )[0],
            0,
        )
        i += 2
        parameter = Parameter(
            name, GUID, acIndex, dcIndex, indexToName, minValue, maxValue, inc, unit
        )
        if subGroupName not in subGroupParameters:
            subGroupParameters[subGroupName] = []
        subGroupParameters[subGroupName].append(parameter)
    return subGroupParameters
