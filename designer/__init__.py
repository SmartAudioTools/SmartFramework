import os
import black
import sys
import math
import itertools
from inspect import getfullargspec
from parse import parse
from importlib import import_module
from qtpy import QtCore, QtWidgets, QtGui, scaled
from PyQt5 import uic
from SmartFramework.string import capitalizeFirstLetter
from SmartFramework.tools.dictionaries import sorted_dict
from SmartFramework.tools.objects import ismethod_methoddescriptor_or_function
from SmartFramework.serialize.tools import class_str_from_class
from SmartFramework.designer.designerParameters import (
    initArgToPropertyFilter,
)
from SmartFramework.files import (
    changeExt,
    joinPath,
    readLines,
    read,
    write,
    name,
    directory,
    chercheExt,
    packagepath_package_subpackage_module_from_Path,
    createFolder,
)


# Gestion de proprietes --------------------

QtClassSubClassAndInitArgs = {
    "PLOT_BASE": ("QtWidgets.QWidget", dict()),
    "QtCore.QObject": (None, dict()),
    "QtWidgets.QWidget": (
        "QtCore.QObject",
        dict(
            enabled=True,
            minimumSize=QtCore.QSize(),
            maximumSize=QtCore.QSize(16777215, 16777215),
            toolTip="",
            layoutDirection=QtCore.Qt.LeftToRight,
            styleSheet="",
            visible=True,
        ),
    ),  # permer de garder nom des QWidget correspondant au contenu d'un QDockWidget et de pouvoir customise styleSheet uniquement pour cet objet
    "QtWidgets.QGLWidget": ("QtWidgets.QWidget", dict()),
    "QtWidgets.QAbstractSpinBox": (
        "QtWidgets.QWidget",
        dict(
            alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft,
            buttonSymbols=0,
            readOnly=False,
            keyboardTracking=True,
        ),
    ),
    "QtWidgets.QSpinBox": (
        "QtWidgets.QAbstractSpinBox",
        dict(prefix="", suffix="", minimum=0, maximum=99, singleStep=1, value=0),
    ),
    "QtWidgets.QDoubleSpinBox": (
        "QtWidgets.QAbstractSpinBox",
        dict(
            decimals=2,
            prefix="",
            suffix="",
            minimum=0.0,
            maximum=99.99,
            singleStep=1.0,
            value=0.0,
        ),
    ),  # sizePolicy, alignment
    "QtWidgets.QAbstractButton": (
        "QtWidgets.QWidget",
        dict(text="", checkable=False, checked=False, autoExclusive=False),
    ),
    "QtWidgets.QPushButton": ("QtWidgets.QAbstractButton", dict()),
    "QtWidgets.QCheckBox": ("QtWidgets.QAbstractButton", dict(checkable=True)),
    "QtWidgets.QLineEdit": ("QtWidgets.QWidget", dict(readOnly=False, text="")),
    "QtWidgets.QFrame": ("QtWidgets.QWidget", dict()),
    "QtWidgets.QLabel": (
        "QtWidgets.QFrame",
        dict(text="", alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft),
    ),
    "QtWidgets.QComboBox": (
        "QtWidgets.QWidget",
        dict(editable=False, maxVisibleItems=10),
    ),
    "QtWidgets.QAbstractSlider": (
        "QtWidgets.QWidget",
        dict(minimum=0, maximum=99, singleStep=1, value=0, orientation=None),
    ),
    "QtWidgets.QSlider": ("QtWidgets.QAbstractSlider", dict(tickInterval=0)),
    "QtWidgets.QDockWidget": (
        "QtWidgets.QWidget",
        dict(
            objectName="",
            windowTitle="",
            features=None,
            floating=True,
            allowedAreas=QtCore.Qt.AllDockWidgetAreas,
        ),
    ),  # [initArgsKeys , initArgsValues]
    "QtWidgets.QVBoxLayout": (None, dict(spacing=-1)),
    "QtWidgets.QHBoxLayout": (None, dict(spacing=-1)),
    "QtWidgets.QGridLayout": (None, dict(spacing=-1)),
    "QtWidgets.QFormLayout": (None, dict(spacing=-1)),
    "QtWidgets.QOpenGLWidget": ("QtWidgets.QWidget", dict()),
    "QtWidgets.QAbstractItemView": ("QtWidgets.QFrame", dict()),
    "QtWidgets.QTreeView": ("QtWidgets.QAbstractItemView", dict()),
    "QtWidgets.QTreeWidget": ("QtWidgets.QTreeView", dict())
    # "QtWidgets.QSplitter"    : [["orientation"],[QtCore.Qt.Vertical]]
}


def reversedEnumerate(L):
    # Only works on things that have a len()
    l = len(L)
    for i, n in enumerate(reversed(L)):
        yield l - i - 1, n


def moveLinesWithToEnd(
    lines, withStrOrList, entete=None, sort=False, stopWithFirst=False
):
    moveLines = []
    stop = False
    if not isinstance(withStrOrList, (list, tuple)):
        withStrOrList = [withStrOrList]
    for i, line in reversedEnumerate(lines):
        if stop:
            break
        for elt in withStrOrList:
            if line.find(elt) != -1:
                del lines[i]
                moveLines.append(line)
                if stopWithFirst:
                    stop = True
                    break
    if sort:
        moveLines.sort()
    if moveLines:
        if entete:
            moveLines.insert(0, entete)
        lines.extend(reversed(moveLines))


def getInstanceProperties(liste, objName):
    instanceProperties = dict()
    lineIndexs = []
    for i, line in enumerate(liste):
        # met au propre les lignes (pas tres optimisé car le fait pour chaque objet)
        line = line.replace(" ", "")

        # cherche les propriété de l'objet
        if compareStartOfLine(line, objName + ".setProperty("):
            # print('trouve .setProperty')
            propertieStart = line.find('("') + 2
            propertieEnd = line.find('"', propertieStart + 3)
            propertie = line[propertieStart:propertieEnd]
            valueStart = propertieEnd + 2
            valueEnd = line.rfind("))")
            valueStr = line[valueStart:valueEnd]
            instanceProperties[propertie] = valueStr
            lineIndexs.append(i)

        elif compareStartOfLine(line, objName + ".set") and not compareStartOfLine(
            line, objName + ".setGeometry"
        ):
            # print('trouve ' + objName + '.set')
            propertieStart = line.find(".set") + 4
            propertieEnd = line.find("(")
            propertie = (
                line[propertieStart].lower() + line[propertieStart + 1 : propertieEnd]
            )
            valueStart = propertieEnd + 1
            valueEnd = line.rfind(")")
            valueStr = line[valueStart:valueEnd]
            if (
                valueStr.find(",") == -1
            ):  # on a un seul argument au setTruc , semble bien une propriété
                instanceProperties[propertie] = valueStr
                lineIndexs.append(i)

    return instanceProperties, lineIndexs


def getInstanceProperties2(liste, objName):
    # instanceProperties = dict()
    # lineIndexPropertieValues = []
    propertieToLineIndexValue = dict()
    for i, line in enumerate(liste):
        # met au propre les lignes (pas tres optimisé car le fait pour chaque objet)
        line = line.strip()

        # cherche les propriété de l'objet
        if compareStartOfLine(line, objName + ".setProperty("):
            # print('trouve .setProperty')
            propertieStart = line.find('("') + 2
            propertieEnd = line.find('"', propertieStart + 3)
            propertie = line[propertieStart:propertieEnd]
            valueStart = propertieEnd + 2
            valueEnd = line.rfind("))")
            valueStr = line[valueStart:valueEnd].strip()
            # instanceProperties[propertie] = valueStr
            propertieToLineIndexValue[propertie] = (line, i, valueStr)

        elif compareStartOfLine(line, objName + ".set") and not compareStartOfLine(
            line, objName + ".setGeometry"
        ):
            # print('trouve ' + objName + '.set')
            propertieStart = line.find(".set") + 4
            propertieEnd = line.find("(")
            propertie = (
                line[propertieStart].lower() + line[propertieStart + 1 : propertieEnd]
            )
            valueStart = propertieEnd + 1
            valueEnd = line.rfind(")")
            valueStr = line[valueStart:valueEnd]
            # if valueStr.find(',') == -1 : # on a un seul argument au setTruc , semble bien une propriété, fout la merde pour des value style QtGui.QClor(255,0,0,150)
            # instanceProperties[propertie] = valueStr
            # lineIndexs.append(i)
            propertieToLineIndexValue[propertie] = (line, i, valueStr)

    return propertieToLineIndexValue


def pyqtProperties_properties_getters_setters_from_class(class_):
    pyqtProperties = []
    properties = []
    getters = {}
    setters = {}
    for base_class in class_.__mro__:
        for key, value in base_class.__dict__.items():
            # print(key)
            if isinstance(value, QtCore.Property):
                pyqtProperties.append(key)
            elif isinstance(value, property):
                properties.append(key)
            elif (
                key.startswith("set")
                and len(key) > 3
                and ismethod_methoddescriptor_or_function(value)
            ):  # and callable(value):
                if key[3] == "_":
                    attribut_name = key[4:]
                elif len(key) > 4 and key[4].isupper():  # nom en majuscules
                    attribut_name = key[3:]
                else:
                    attribut_name = key[3].lower() + key[4:]
                if attribut_name not in setters:
                    # on a peut etre definit deux setters set_x et setX dans deux classes de base différente, on gard la p
                    setters[attribut_name] = value
                    for getter_name in (attribut_name, "g" + key[1:], "is" + key[3:]):
                        getter_methode = getattr(base_class, getter_name, None)
                        if getter_methode is not None:
                            if (
                                getter_methode not in getters
                                and ismethod_methoddescriptor_or_function(
                                    getter_methode
                                )
                            ):  # and callable(getter_methode):
                                getters[attribut_name] = getter_methode
                                break
    for property_ in properties + pyqtProperties:
        if property_ in setters:
            del setters[property_]
            if property_ in getters:
                del getters[property_]
    return (
        sorted(pyqtProperties),
        sorted(properties),
        sorted_dict(getters),
        sorted_dict(setters),
    )


def getAndDelInstanceProperties(liste, objName):
    properties, lineIndexs = getInstanceProperties(liste, objName)
    # suprime les propriété
    lineIndexs.reverse()
    for i in lineIndexs:
        del liste[i]
    return properties


def getIndexCreation(liste, objName):
    for i, line in enumerate(liste):
        line = line.replace(" ", "")
        if compareStartOfLine(line, objName + "="):
            return i
    return None


def tinySetItems(lines, objsDict):
    # met en forme les .addItem("") et .setItemText(0, "BAYER")
    for objName, objClasse in objsDict.items():
        indexToDel = []
        items = []
        for i, line in enumerate(lines):
            # met au propre les lignes (pas tres optimisé car le fait pour chaque objet)
            line = line.strip()
            # cherche les .setItemText
            if compareStartOfLine(line, objName + ".setItemText("):
                valueStart = line.find('"')
                valueEnd = line.rfind(")")
                valueStr = line[valueStart:valueEnd]
                items.append(valueStr)
                indexToDel.append(i)
            # cherche les .addItem("")
            if compareStartOfLine(line, objName + '.addItem("")'):
                indexToDel.append(i)
        indexToDel.sort()
        indexToDel.reverse()
        for i in indexToDel:
            del lines[i]
        if items:
            indexCreation = getIndexCreation(lines, objName)
            if (
                False
            ):  # viré car l'objet n'a pas forcement items en argument de son __init__
                line = lines[indexCreation]
                parenteseFin = line.rfind(")")
                line = line[:parenteseFin]
                if line[-1] != "(":
                    line = line + ","
                line = line + "items=[%s])" % (",".join(items))
                lines[indexCreation] = line
            else:
                lines.insert(
                    indexCreation + 1,
                    "        %s.setItems([%s])" % (objName, ",".join(items)),
                )


def tinySetProperties(liste, objsDict):
    for objName, objClasse in objsDict.items():
        # analyse properties
        propertieToLineIndexValue = getInstanceProperties2(liste, objName)
        # retrouve index de creation de l'objet
        indexCreation = getIndexCreation(liste, objName)
        # recréer propriétés soit en tant qu'argument de creation soit en propriété (avec un = )
        if propertieToLineIndexValue:
            indexToDel = []
            initArgsToAdd = dict()
            initArgs = getClasseInitArgs(objClasse)
            if (
                "styleSheet" in propertieToLineIndexValue
            ):  # ajoute objectName comme initArg si on l'utilise dans la proprieté styleSheet
                if propertieToLineIndexValue["objectName"][2]:
                    if (
                        propertieToLineIndexValue["objectName"][2].strip('"')
                        in propertieToLineIndexValue["styleSheet"][2]
                    ):
                        initArgs["objectName"] = ""
            for propertie, lineIndexValueStr in propertieToLineIndexValue.items():
                line, index, valueStr = lineIndexValueStr
                if propertie in initArgs.keys():  # propertie in initArgsKeys:
                    indexToDel.append(index)  # il faut supprimer la ligne
                    try:
                        if (
                            valueStr == initArgs[propertie]
                            or eval(valueStr) == initArgs[propertie]
                        ):
                            # elle correspond à la valeure par defaut ... ne fait rien:
                            pass
                        else:
                            initArgsToAdd[propertie] = valueStr
                    except:
                        initArgsToAdd[propertie] = valueStr
                elif propertie not in (
                    "objectName",
                    "sizePolicy",
                    "contentsMargins",
                    "widget",
                    "stretch",
                ):
                    print(
                        "impossible de trouver d'argument d'__init__ pour la propriete %s de la class %s"
                        % (propertie, objClasse)
                    )
                    # demande de la recree sous la forme xxx.propertie = .....
                    # liste.insert(indexCreation + 1,'        ' + objName + '.' + propertie + ' = ' + valueStr)

            indexToDel.sort()
            indexToDel.reverse()
            for i in indexToDel:
                del liste[i]

            # demande de la recréer en tant qu'argument
            if initArgsToAdd != dict():
                line = liste[indexCreation]
                parenteseFin = line.rfind(")")
                line = line[:parenteseFin]
                # for key in initArgsToAdd.keys():
                #    if key not in initArgs:
                #        raise Exception
                for key in initArgs:
                    if key in initArgsToAdd:
                        valueStr = initArgsToAdd[key]
                        # for key, valueStr in initArgsToAdd.items():
                        if line[-1] != "(":
                            line = line + ","
                        line = line + key + "=" + valueStr
                liste[indexCreation] = line + ")"


# Gestion de chemins de fichiers -------------


# Gestion de lignes de text -------------


def replaceLine(liste, string, string2):
    index = findLine(liste, string)
    if index != -1:
        if type(string2) is list:
            del liste[index]
            inserts(liste, index, string2)
        else:
            liste[index] = string2


def removeDoubleNewLine(liste):
    lastElt = None
    newListe = []
    for elt in liste:
        if elt != "" or lastElt != "":
            newListe.append(elt)
        lastElt = elt
    return newListe


def replaceInLines(liste, string, string2):
    for i, line in enumerate(liste):
        if line.find(string) != -1:
            liste[i] = line.replace(string, string2)


def inserts(l, index, elts):
    for elt in elts[::-1]:
        l.insert(index, elt)


def delLineAndBefore(liste, string):
    index = findLine(liste, string)
    if index != -1:
        del liste[index - 1 : index + 1]
    else:
        pass


def delLine(liste, string):
    index = findLine(liste, string)
    if index != -1:
        del liste[index]
    else:
        pass


def delLines(liste, string):
    indexs = findLines(liste, string)
    indexs.reverse()
    for index in indexs:
        del liste[index]


def compareStartOfLine(line, start):
    line = line.replace(" ", "")
    start = start.replace(" ", "")
    return line.startswith(start)


def findLine(liste, string):
    for i, line in enumerate(liste):
        if line.find(string) != -1:
            return i
    return -1


def findLines(liste, string):
    indexs = []
    for i, line in enumerate(liste):
        if line.find(string) != -1:
            indexs.append(i)
    return indexs


def sansEspaces(liste):
    listeSansEspaces = []
    for line in liste:
        listeSansEspaces.append(line.replace(" ", ""))
    return listeSansEspaces


# Fonctions pour trouver les objets python et leurs attribut par defaut ----------------


def getPluginClasses():
    # crée une liste de Classes correspondant à des plugins python
    classes = []
    for pluginPath in chercheExt(joinPath(directory(__file__), "plugins"), "py"):
        plugin_filename = name(pluginPath)
        if len(plugin_filename) > 7 and plugin_filename[-7:] == "~plugin":
            class_name = plugin_filename[:-7].split("~")[-1]
            classes.append(class_name)
    return classes


def getDIClasses():
    return [
        class_name for class_name in getPluginClasses() if not class_name.endswith("UI")
    ]


def getClassePath(class_str):
    pluginPaths = chercheExt(joinPath(directory(__file__), "plugins"), "py")
    for pluginPath in pluginPaths:
        if pluginPath.endswith("~" + class_str + "~plugin.py"):
            # pluginLines = readLines(pluginPath, iterator=False)
            # line = pluginLines[pluginLines.index("    def includeFile(self):") + 1]
            # pyObjpathWithoutExt = base_repertory + line.split('"')[1].replace(".", "/"
            pathEnd = name(pluginPath)[:-7].replace("~", "/")
            for folder, ext in itertools.product(sys.path, ("pyw", "py")):
                pathTest = joinPath(folder, pathEnd, ext)
                if os.path.exists(pathTest):
                    return pathTest
    raise Exception(
        "impossible de trouver le path du module correspondant à %s" % pluginPath
    )


def getClasseInitArgs(classe, inherited=True):
    if classe in QtClassSubClassAndInitArgs:
        subClass, classInitArgs = QtClassSubClassAndInitArgs[classe]
        initArgs = dict()
        if subClass is not None:
            initArgs.update(getClasseInitArgs(subClass))
        initArgs.update(classInitArgs)
        return initArgs
    # ouverture du fichier
    path = getClassePath(classe)
    moduleStrListe = readLines(path, iterator=False)
    return analyseInitArgs(moduleStrListe, classe, inherited=inherited)


def analyseInitArgs(moduleStrListe, objClasse, inherited=True):
    # print('\n'.join(moduleStrListe))
    # analyse du fichier
    # indexClass =
    initArgs = dict()
    indexClass = findLine(moduleStrListe, "class " + objClasse)
    if indexClass == -1:
        raise Exception(
            'impossible de trouver la ligne commencant par "class %s" dans le fichier contenant la classe'
            % objClasse
        )
    classLine = moduleStrListe[indexClass]
    initStartIndex = findLine(moduleStrListe[indexClass:], "def __init__(") + indexClass
    if initStartIndex != -1:
        initEndIndex = findLine(moduleStrListe[initStartIndex:], "):") + initStartIndex
        initLines = [
            l.split("#")[0].replace(" ", "")
            for l in moduleStrListe[initStartIndex : initEndIndex + 1]
        ]
        initLine = "".join(initLines)

    if inherited:
        if initStartIndex == -1 or initLine.find("**") != -1:
            inheritClasses = classLine[
                classLine.find("(") + 1 : classLine.rfind(")")
            ].split(",")
            for inheritClasse in inheritClasses:
                inheritClasse = inheritClasse.strip()
                try:
                    initArgs.update(getClasseInitArgs(inheritClasse))
                except:
                    pass

    if initStartIndex != -1:
        indexStart = initLine.find(",") + 1
        indexEnd = initLine.rfind(")")

        argStr = initLine[indexStart:indexEnd]
        # pour suporter formatage black avec des "," qui trainent à la fin

        argStr = argStr.strip().rstrip(",")
        # print(argStr)

        # initArgs = dict()
        initArgsKeys = []
        initArgsValues = []
        if argStr.find(",*") != -1:
            indexVirguleOrComaAfter = argStr.find(",*")
        else:
            indexVirguleOrComaAfter = len(argStr)

        indexEgal = argStr.rfind("=")
        while indexEgal != -1:
            indexVirguleBefore = argStr.rfind(
                ",", 0, indexEgal
            )  # me zero pour le start , pour pouvoir demander un stop
            key = argStr[indexVirguleBefore + 1 : indexEgal]
            value = argStr[indexEgal + 1 : indexVirguleOrComaAfter]
            indexVirguleOrComaAfter = indexVirguleBefore
            if key != "parent":
                # initArgs[key] = value
                initArgsKeys.insert(0, key)
                initArgsValues.insert(0, value)
            indexEgal = argStr.rfind("=", 0, indexEgal - 1)
        initArgs.update(dict(zip(initArgsKeys, initArgsValues)))
    return initArgs


def findInstances(liste, classes):
    """retourne dictionnaire[noms d'instances] = classe , d\'une liste de classes"""

    listeSansEspaces = sansEspaces(liste)
    objsDict = dict()  # dictionnaire { nomInstance : nomClasse }
    for classe in classes:
        for i, line in enumerate(listeSansEspaces):
            objNameEnd = line.find("=" + classe + "(")
            if objNameEnd != -1:
                # recuper nom de l'instant de l'objet
                objNameStart = 0
                objName = line[objNameStart:objNameEnd]
                objsDict[objName] = classe
    return objsDict


def findOneClasse(liste, classe):
    """retourne la liste de noms d'instances d'un seule classe"""
    listeSansEspaces = sansEspaces(liste)
    objsListe = []
    for i, line in enumerate(listeSansEspaces):
        objNameEnd = line.find("=" + classe + "(")
        if objNameEnd != -1:
            objNameStart = 0
            objName = line[objNameStart:objNameEnd]
            objsListe.append(objName)
    return objsListe


def findQtInstances(liste):
    QtClassesIter = QtClassSubClassAndInitArgs.keys()
    return findInstances(
        liste, QtClassesIter
    )  # recherche ses classes dans le code generé par uic


def findPluginInstances(liste):
    pluginClasses = (
        getPluginClasses()
    )  # crée une liste de Classes correspondant à des plugins python
    return findInstances(
        liste, pluginClasses
    )  # recherche ses classes dans le code generé par uic


def findDIs(liste):
    DIClasses = (
        getDIClasses()
    )  # crée une liste de Classes correspondant à des plugins python
    return findInstances(
        liste, DIClasses
    )  # recherche ses classes dans le code generé par uic


def findUI(liste):
    for i, line in enumerate(liste):
        line = line.replace(" ", "")
        if line.find("UI(") != -1 or (
            line.find("=QtWidgets.") != -1 and line.find("=QtGui.QColor") == -1
        ):
            # print('trouve UI : '+ line)
            return True
    return False


def findImports(liste):
    indexs = []
    for i, line in enumerate(liste):
        if line.startswith("from "):
            indexs.append(i)
    return indexs


# ----------------------------------------------


def findInputs(liste):
    return findOneClasse(liste, "Input")


def findOutputs(liste):
    return findOneClasse(liste, "Output")


def findInputsFromConnexions(liste, classString):
    inputs = []
    for i, line in enumerate(liste):
        senderIndex = line.find("QtCore.QObject.connect(classString")
        if senderIndex != -1:
            senderStart = senderIndex + 23
            senderEnd = line.find(', QtCore.SIGNAL("')
            sender = line[senderStart:senderEnd]
            inputs.append(sender)
    return inputs


def findOutputsFromConnexions(liste, classString):
    outputs = []
    for i, line in enumerate(liste):
        senderIndex = line.find("QtCore.QObject.connect(classString")
        if senderIndex != -1:
            senderStart = senderIndex + 23
            senderEnd = line.find(', QtCore.SIGNAL("')
            sender = line[senderStart:senderEnd]
            outputs.append(sender)
    return outputs


def analyseOneConnexionRaw(string):
    string = string.rstrip(" # type: ignore")
    try:
        senderAndSignal, signature, slot = parse(
            "        {}[{}].connect({})", string
        ).fixed

    except:
        senderAndSignal, slot = parse("        {}.connect({})", string).fixed
        signature = ""
    sender, signal = senderAndSignal.rsplit(".", 1)
    newSignatureElts = []
    for signatureElt in signature.split(","):
        signatureElt = signatureElt.strip("'")
        if signatureElt == "PyQt_PyObject":
            signatureElt = "object"
        elif signatureElt == "QString":
            signatureElt = "str"
        elif signatureElt == "double":
            signatureElt = "float"
        elif signatureElt == "QColor":
            signatureElt = "QtGui.QColor"
        elif signatureElt == "QTime":
            signatureElt = "QtCore.QTime"
        newSignatureElts.append(signatureElt)
    newSignature = ",".join(newSignatureElts)
    return [sender, signal, newSignature, slot]


# CONVERSIONS _------------------------------------------------------


def pythonToPlugin(path):
    designerDirectory = directory(__file__)
    (
        packagepath,
        package,
        sub_package,
        module,
    ) = packagepath_package_subpackage_module_from_Path(path)
    Name = capitalizeFirstLetter(name(path))

    # plugin PyQt
    pluginStr = read(joinPath(designerDirectory, "QObjectplugin.py")).format(**locals())
    black_string = black.format_str(pluginStr, mode=black.Mode(line_length=88))
    module_ = module.replace(".", "~")
    pluginPath = f"{packagepath}/Qt_plugins/{module_}~plugin.py"
    createFolder(pluginPath)
    print("write ", pluginPath)
    write(pluginPath, black_string)

    # plugin PySide
    pluginStr = read(joinPath(designerDirectory, "registerQObject.py")).format(
        **locals()
    )
    black_string = black.format_str(pluginStr, mode=black.Mode(line_length=88))
    module_ = module.replace(".", "~")
    pluginPath = f"{packagepath}/Qt_plugins/register~{module_}.py"
    createFolder(pluginPath)
    print("write ", pluginPath)
    write(pluginPath, black_string)


def pyqtPopertyFromInitArgsGenerator(moduleStrListe, className, importAndInitLines):
    objectEnd = findObjectEnd(moduleStrListe, className)

    # cree une liste des proprietes pyqt deja existante
    indexs = findLines(moduleStrListe, "QtCore.Property(")
    listeProperties = []
    for index in indexs:
        line = moduleStrListe[index]
        indexEnd = line.find("=", 1)
        name = line[:indexEnd]
        name = name.replace(" ", "")
        listeProperties.append(name)

    # cree un dictionnaire  des setter
    indexs = findLines(moduleStrListe, "def set")
    dictSetters = {}
    for index in indexs:
        line = moduleStrListe[index]
        indexStart = line.find("def set", 1) + 7
        indexEnd = line.find("(", 1)
        name = line[indexStart:indexEnd]
        bodyLines = []
        for bodyLine in moduleStrListe[index + 1 : objectEnd]:
            if not bodyLine.startswith("    def "):
                bodyLines.append(bodyLine)
        dictSetters[name] = bodyLines

    # cree un dictionnaire des getter
    indexs = findLines(moduleStrListe, "def get")
    dictGetters = {}
    for index in indexs:
        line = moduleStrListe[index]
        indexStart = line.find("def get", 1) + 7
        indexEnd = line.find("(", 1)
        name = line[indexStart:indexEnd]
        bodyLines = []
        for bodyLine in moduleStrListe[index + 1 : objectEnd]:
            if not bodyLine.startswith("    def "):
                bodyLines.append(bodyLine)
        dictGetters[name] = bodyLines

    # cree 2 listes  avec initArgs et valeures par defaut (sous forme de string)

    initArgs = analyseInitArgs(moduleStrListe, className, inherited=False)
    # print(initArgsKeys,initArgsValues)
    # regarde si on a utilisé des attribut pour stocker les initArgs et si oui sous la forme arg ou _arg
    if (
        findLine(moduleStrListe, "self.__dict__.update(locals())") != -1
        or findLine(moduleStrListe, "addArgs(locals())") != -1
    ):
        attributTypes = "arg"
    elif findLine(moduleStrListe, "add_Args(locals())") != -1:
        attributTypes = "_arg"
    else:
        attributTypes = None
    # print(initArgsDict)
    # analyse existance de propriete/setter/getter pour chaqun des arguments

    codeToAdd = []
    importToAdd = []
    for key, value in initArgs.items():
        if (
            (not key.startswith(initArgToPropertyFilter))
            and (key != "objectName")
            and (value != "None")
        ):  # key != "objectName" sert pour eviter d'ecraser la propriete objectName qui herité de QWidget , ce qui foutrait la merde dans QtDesigner
            Key = key[0].upper() + key[1:]

            # determine le nom de l'attribut correspondant
            if not attributTypes:
                if findLine(moduleStrListe, "self._" + key) != -1:
                    attributType = "_arg"
                elif findLine(moduleStrListe, "self." + key) != -1:
                    attributType = "arg"
                else:
                    print("WARNING: not attribut for " + key + " founded")
                    attributType = "arg"
                    # continue
            else:
                attributType = attributTypes

            if key not in listeProperties:  # .count(key) == 0 :
                # print('tente creer proprietes')
                if Key in dictSetters:
                    setter = "set" + Key
                    if findLine(dictSetters[Key], "self." + key) != -1:
                        print(
                            "ERROR: "
                            + key
                            + " will be transforme in Property for Qt Designer intergration. To avoid inifinit loop use self._"
                            + key
                            + " = value or self.__dict__['"
                            + key
                            + "'] = value instead of self."
                            + key
                            + " = value"
                        )
                        os.system("pause")
                else:
                    setter = "set" + Key
                    codeToAdd.append("def set" + Key + "(self,value):")
                    if attributType == "_arg":
                        codeToAdd.append("    self._" + key + " = value")
                    else:
                        codeToAdd.append("    self.__dict__['" + key + "'] = value")
                if Key in dictGetters:
                    getter = "get" + Key
                    if findLine(dictGetters[Key], "self." + key) != -1:
                        print(
                            "ERROR: "
                            + key
                            + " will be transforme in Property for Qt Designer intergration. To avoid inifinit loop use self._"
                            + key
                            + " = value or self.__dict__['"
                            + key
                            + "'] = value instead of self."
                            + key
                            + " = value"
                        )
                        os.system("pause")
                else:
                    getter = "get" + Key
                    codeToAdd.append("def get" + Key + "(self):")
                    if attributType == "_arg":
                        codeToAdd.append("    return self._" + key)
                    else:
                        codeToAdd.append("    return self.__dict__['" + key + "']")
                try:
                    classStr = classStrFromEval(value, importToAdd, importAndInitLines)
                except:
                    raise Exception(
                        "impossible d'évaluer la proriete %s qui a la valeure %s"
                        % (key, str(value))
                    )
                codeToAdd.append(
                    key
                    + " = QtCore.Property("
                    + classStr
                    + ", "
                    + getter
                    + ", "
                    + setter
                    + ")"
                )

    if importToAdd:
        moduleStrListe.insert(
            1, "\n".join(importToAdd)
        )  # ne sait plus exactement à quoi ca sert... permet de redefinir chemin du complet si dans objet d'origine chemin relatif par rapport au module

    if codeToAdd:
        for line in moduleStrListe:
            if line.startswith("from ") and ("QtCore" in line):
                break
        else:
            moduleStrListe.insert(1, "from qtpy import QtCore")
        moduleStrListe.insert(
            findObjectEnd(moduleStrListe, className), "    " + "\n    ".join(codeToAdd)
        )
        return 1

    else:
        return 0


def pyqtPopertyFromInitArgsGenerator2(class_):
    # cree une liste des proprietes pyqt deja existante
    (
        pyqtProperties,
        listeProperties,
        dictGetters,
        dictSetters,
    ) = pyqtProperties_properties_getters_setters_from_class(class_)

    # cree 2 listes  avec initArgs et valeures par defaut (sous forme de string)

    (
        args,  # list of the parameter names.
        varargs,  # name of the * parameter or None
        varkw,  # name of the ** parameter or None
        defaults,  # n-tuple of the default values of the last n parameters.
        kwonlyargs,  # list of keyword-only parameter names.
        kwonlydefaults,  # dictionary mapping names from kwonlyargs to defaults.
        annotations,  # dictionary mapping parameter names to annotations.
    ) = getfullargspec(class_.__init__)
    if len(args) > 1:
        initArgs = dict(zip(args[1:], defaults))
        new_dict = dict(class_.__dict__)
        for key, value in initArgs.items():
            if (
                (not key.startswith(initArgToPropertyFilter))
                and (key not in ["objectName", "parent"])
                and (value != None)
            ):  # key != "objectName" sert pour eviter d'ecraser la propriete objectName qui herité de QWidget , ce qui foutrait la merde dans QtDesigner
                if key not in pyqtProperties:
                    # print('tente creer proprietes')
                    if key in dictSetters:
                        setter = dictSetters[key]
                        # setter = "set" + Key
                        # if findLine(dictSetters[Key], "self." + key) != -1:
                        #    print(
                        #        "ERROR: "
                        #        + key
                        #        + " will be transforme in Property for Qt Designer intergration. To avoid inifinit loop use self._"
                        #        + key
                        #        + " = value or self.__dict__['"
                        #        + key
                        #        + "'] = value instead of self."
                        #        + key
                        #        + " = value"
                        #    )
                        #    os.system("pause")
                    else:

                        def setter(self, value, name=key):
                            if name in self.__dict__:
                                self.__dict__[name] = value
                            else:
                                self.__dict__["_" + name] = value

                    if key in dictGetters:
                        # if Key in dictGetters:
                        getter = dictGetters[key]
                        # getter = "get" + Key
                        # if findLine(dictGetters[Key], "self." + key) != -1:
                        #    print(
                        #        "ERROR: "
                        #        + key
                        #        + " will be transforme in Property for Qt Designer intergration. To avoid inifinit loop use self._"
                        #        + key
                        #        + " = value or self.__dict__['"
                        #        + key
                        #        + "'] = value instead of self."
                        #        + key
                        #        + " = value"
                        #    )
                        #    os.system("pause")
                    else:

                        def getter(self, name=key):
                            try:
                                return self.__dict__["_" + name]
                            except:
                                try:
                                    return self.__dict__[name]
                                except:
                                    return value
                                    # raise Exception(
                                    #    f"no atttribut for {class_.__name__}.{name}"
                                    # )

                    # to_exec = f"class_.{key} = QtCore.Property(type(value), getter, setter)"
                    # print(to_exec)
                    # exec(to_exec)
                    new_dict[key] = QtCore.Property(
                        type(value), getter, setter
                    )  # ne marche pas
        else:
            # bizarre que ce soit necessaire pour ajouter le properties pyqt
            class_ = type(
                class_.__name__,
                class_.__bases__,
                new_dict,
            )
    return class_


def class_from_class_str(string):
    # il ne faut pas mettre en caching sinon ne peut pas bidouiller class_from_class_str_dict
    path_name = string.rsplit(".", 1)
    if len(path_name) == 2:
        path, name = path_name
        try:
            return getattr(import_module(path), name)
        except ModuleNotFoundError:
            path_name2 = path.rsplit(".", 1)
            if len(path_name2) == 2:
                path2, name2 = path_name2
                return getattr(getattr(import_module(path2), name2), name)
            raise
    else:
        return __builtins__[string]


def replaceQObjectByQWidget(class_):
    if class_ is QtCore.QObject:
        return QtWidgets.QWidget
    elif issubclass(class_, QtCore.QObject):
        return type(
            class_.__name__,
            tuple((replaceQObjectByQWidget(elt) for elt in class_.__bases__)),
            dict(class_.__dict__),
        )
    else:
        return class_


def transformClassForQtDesigner(class_):
    """add properties from init args and transform QObject to QWidget it neeede for QtDesigner"""
    # pyqtPopertyFromInitArgsGenerator2(class_)
    # print(class_.__mro__)
    if not issubclass(class_, QtWidgets.QWidget):
        class_.sizeHint = sizeHint
        class_.paintEvent = paintEvent
        class_ = replaceQObjectByQWidget(class_)
    # print(class_.__mro__)
    class_ = pyqtPopertyFromInitArgsGenerator2(class_)
    return class_


def classStrFromEval(s, importToAdd, importAndInitLines):
    try:
        evalued = eval(s)
    except:
        # for line in importAndInitLines:
        try:
            exec("\n".join(importAndInitLines))
            evalued = eval(s)
        except:
            print("""impossible d'evaluer l'arguemnt par defaut "%s" du __init__""" % s)
            raise
    class_ = evalued.__class__
    if class_.__module__ != "builtins":
        importToAdd.append(f"import {class_.__module__}")
    return class_str_from_class(class_)


def findObjectEnd(liste, className):
    inObject = False
    for i, line in enumerate(liste):
        if inObject:
            if line != "":
                if line[0] in " #\t)":
                    lastI = i
                else:
                    return lastI + 1
        elif line.find("class " + className + "(") == 0:
            inObject = True
    return i + 1


def findInitStartEnd(liste, className):
    inObject = False
    start = None
    for i, line in enumerate(liste):
        if inObject:
            if start is not None:
                if line != "":
                    if line[0] in " #\t" and not line.startswith("    def"):
                        lastI = i
                    else:
                        return start, lastI + 1
            if line.startswith("    def __init__("):
                start = i
        elif line.find("class " + className + "(") == 0:
            inObject = True
    return start, i + 1


def ui2uic(uiFileName, pyFileName=None):
    uiFile = open(uiFileName, "r", encoding="utf-8", newline="")
    if not pyFileName:
        pyFileName = changeExt(uiFileName, "py")
    pyFile = open(pyFileName, "w", encoding="utf-8-sig", newline="\n")
    # methode qui génère le code Python à partir d'un dichier.ui Qt Designer.
    uic.compileUi(uiFile, pyFile, execute=False)
    pyFile.close()
    uiFile.close()


def sizeHint(self):
    content_width = QtGui.QFontMetrics(self.font()).width(self.__class__.__name__)
    height = scaled(7) * 5
    if hasattr(self, "__icon__") and not self.__icon__.isNull():
        content_width += height + scaled(5)
    return QtCore.QSize(math.ceil((content_width + scaled(5)) / 10) * 10, height)


def paintEvent(self, event):
    painter = QtGui.QPainter(self)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    penWidth = 1.0
    halfPenWidth = penWidth / 2
    pen = QtGui.QPen()
    pen.setWidthF(penWidth)
    rect = QtCore.QRectF(self.rect())
    insideRect = rect.adjusted(halfPenWidth, halfPenWidth, -halfPenWidth, -halfPenWidth)
    painter.setPen(pen)
    path = QtGui.QPainterPath()
    path.addRoundedRect(insideRect, scaled(6), scaled(6))
    painter.fillPath(path, QtGui.QColor(255, 255, 255, 150))
    painter.drawPath(path)
    text = self.__class__.__name__
    if hasattr(self, "__icon__") and not self.__icon__.isNull():
        self_rect = self.rect()
        marge = scaled(5)
        icon_rect = QtCore.QRect(
            self_rect.x() + marge,
            self_rect.y() + marge,
            self_rect.height() - 2 * marge,
            self_rect.height() - 2 * marge,
        )
        text_rect = self_rect.adjusted(self_rect.height() + 2, 0, 0, 0)
        self.__icon__.paint(painter, icon_rect)
        painter.drawText(text_rect, int(QtCore.Qt.AlignVCenter), text)
    else:
        painter.drawText(
            self.rect(), int(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter), text
        )

    """  #plante sur les nom longs _?_
        self.style().drawItemText(
            painter,
            self.rect(),
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
            QtWidgets.QStyleOption().palette,
            self.isEnabled(),
            text,
            self.foregroundRole(),
        )"""


# OLDIES ----------------------------------------------------------------------


def ui2uicObject(File, compil=False):
    if compil:
        ui2uic(File, "Patch_ui.py")
        from Patch_ui import (
            Ui_widget,
        )  # Ui_Dialog, Ui_Form ou  Ui_MainWindow  : definit dans Designer.

        # os.remove(file+'.c')
        uiClass = Ui_widget  # renomage pour convenir a mes conventions perso
        BaseClass = QtWidgets.QWidget
    else:
        uiClass, BaseClass = uic.loadUiType(File)

    class ui(BaseClass, uiClass):
        def __init__(self, parent=None):
            BaseClass.__init__(
                self, parent
            )  # cree un widget du type definit dans Designer (QForm, QWidget ou QMainWindow)
            self.setupUi(
                self
            )  # configure le widget selon ce model contenu dans uiClass

        def closeEvent(
            self, QCloseEven
        ):  # redefinition du slot closeEvent, pour emetre un signal (pas de signal emit par defaut ???)
            # QCloseEven.ignore() # si on veut empecher fermeture fenetre:
            QCloseEven.accept()
            self.emit(
                QtCore.SIGNAL("closeApplication()")
            )  # permet de fermet l'audio etc en meme temps

    return ui()
