import black
import io
from SmartFramework.string import extract
from SmartFramework.files import (
    splitPath,
    joinPath,
    chercheExt,
    write,
    readLines,
    read,
)
from SmartFramework.designer import (
    tinySetProperties,
    ui2uic,
    uic,
    findLine,
    delLine,
    delLineAndBefore,
    delLines,
    findDIs,
    findImports,
    findLines,
    findPluginInstances,
    analyseOneConnexionRaw,
    inserts,
    replaceInLines,
    replaceLine,
    findUI,
    removeDoubleNewLine,
    findQtInstances,
    moveLinesWithToEnd,
    designerParameters,
    tinySetItems,
)
import os

os.environ["QT_API"] = "PyQt5"


def uiToPython(path, minimizeInSysTray=False):
    # compile le fichier ui en fichier python

    widgetDirectory, widgetName, extension = splitPath(path)

    # remplacement dans fichier ui des
    replacements = {
        '<layout class="QVBoxLayout" name="verticalLayout': '<layout class="QVBoxLayout" name="_verticalLayout',
        '<layout class="QHBoxLayout" name="horizontalLayout': '<layout class="QHBoxLayout" name="_horizontalLayout',
        '<layout class="QFormLayout" name="formLayout': '<layout class="QFormLayout" name="_formLayout',
        '<layout class="QGridLayout" name="gridLayout': '<layout class="QGridLayout" name="_gridLayout',
    }
    ui_str = ui_str_origin = read(path, encoding="utf_8")
    for str_1, str_2 in replacements.items():
        ui_str = ui_str.replace(str_1, str_2)
    if ui_str != ui_str_origin:
        write(path, ui_str, encoding="utf_8", newline="\r\n")

    # Compilation du fichier ui ------------------------------------

    if (
        designerParameters.compileUiInUicFile
    ):  # compile le fichier ui avec uic dans un fichier intermediaire
        uicPath = joinPath(widgetDirectory, widgetName + "Uic", "py")
        ui2uic(path, uicPath)
        uicLines = readLines(uicPath, encoding="utf-8", iterator=False)
    else:
        uicFile = io.StringIO()
        with open(path, "r", encoding="utf-8", newline="") as uiFile:
            uic.compileUi(uiFile, uicFile, execute=False)
        uicFile.seek(0)
        uicLines = uicFile.read().splitlines()

    # Trouve nom de la forme utilisee dans QtDesigner
    classLineIndex = findLine(uicLines, "class Ui_")
    classString = uicLines[classLineIndex]
    debut = classString.find("_", 1)
    fin = classString.find("(", 1)
    widget = classString[debut + 1 : fin]

    # widget = "Webcam"
    # print(widget)

    # supression -------------------------------------------

    # suppression des 8 premieres lignes de commentaire
    del uicLines[0:8]

    # supression des lignes de definition de  _fromUtf8 et de l'espace apres
    indexDef = findLine(uicLines, "    _fromUtf8 = QtCore.QString.fromUtf8")
    if indexDef != -1:
        del uicLines[indexDef - 1 : indexDef + 5]

    # supression des lignes de definition de  _translate  et de l'espace apres
    indexDef = findLine(uicLines, "    _encoding = QtWidgets.QApplication.UnicodeUTF8")
    if indexDef != -1:
        del uicLines[indexDef - 1 : indexDef + 7]

    # suppressions de lignes contenant ....
    delLine(uicLines, "from SmartFramework.designer.Output import Output")
    delLine(uicLines, "from SmartFramework.designer.Input import Input")
    delLineAndBefore(uicLines, "    def retranslateUi(self,")
    delLine(uicLines, "        _translate = QtCore.QCoreApplication.translate")
    delLine(uicLines, "        pass")
    delLines(uicLines, "QtCore.QMetaObject.connectSlotsByName(")
    delLine(uicLines, ".setWindowTitle(")
    delLineAndBefore(uicLines, "self.retranslateUi(")

    # supression des setGeometry et raise_()pour les objet non graphique .... comment les reconnaitre ? ceux qui sont dans repertoir DI ?
    DINames = findDIs(uicLines)
    for DIName in DINames:
        delLine(uicLines, DIName + ".setGeometry")
        delLine(uicLines, DIName + ".raise_()")

    # Deplacement ---------------------------------------------------

    # deplace les imports (sinon il les met en plein milieu )
    indexImports = findImports(uicLines)
    # if widget == "MainWindow":
    uicLines[indexImports[0]] += ", API_NAME"
    reversedImportLines = []
    for i in reversed(
        indexImports
    ):  # commece a un, car indexImports[0] corespond à from qtpy import QtCore,QtGui,QtWidgets qui est déjà bien placé et auquel on ne veut pas toucher
        line = uicLines[i].replace("PyQt5", "qtpy")
        reversedImportLines.append(line)
        del uicLines[i]

    if uicLines[-1] == "":  # suprime ligne vide a la fin si y'a
        del uicLines[-1]

    # remonte les QDock.setWidget(..) pour eviter à partir de PyQt 5.12 bug d'update qui ne declanche pas de repaint pour PlotUI en mode OpenGl  -----------

    QDockWidgetLineIndexs = findLines(uicLines, "QtWidgets.QDockWidget(")
    for QDockWidgetLineIndex in QDockWidgetLineIndexs:
        line = uicLines[QDockWidgetLineIndex]
        QDockWidgetName = line.split("=")[0].strip()
        setWidgetLineIndex = findLine(uicLines, f"{QDockWidgetName}.setWidget(")
        setWidgetLine = uicLines[setWidgetLineIndex]
        WidgetName = extract(setWidgetLine, "(", ")")
        WidgetCreationLineIndex = findLine(
            uicLines, f"{WidgetName} = QtWidgets.QWidget()"
        )
        del uicLines[setWidgetLineIndex]
        uicLines.insert(WidgetCreationLineIndex + 1, setWidgetLine)

    # remplacements ---------------------------------------------------------
    fromUtf8Lines = findLines(uicLines, "_fromUtf8(")
    translateFormLines = findLines(uicLines, '_translate("Form",')
    translateSelfLines = findLines(uicLines, '_translate("self",')
    translateMainWindowLines = findLines(uicLines, '_translate("MainWindow",')

    for i in translateFormLines:
        uicLines[i] = uicLines[i].replace('_translate("Form", ', "").replace('")', '"')
    for i in translateSelfLines:
        uicLines[i] = uicLines[i].replace('_translate("self", ', "").replace('")', '"')
    for i in translateMainWindowLines:
        uicLines[i] = (
            uicLines[i].replace('_translate("MainWindow", ', "").replace('")', '"')
        )
    for i in fromUtf8Lines:
        uicLines[i] = uicLines[i].replace('_fromUtf8("', '"').replace('")', '"')

    # Analyse les connections -------------------------------------------------

    # recopie lignes de old connexion et les supprime dans uicLines -----------

    # index des connections oldstyle
    indexConnexions = findLines(uicLines, ".connect(")

    # recopie connections
    linesConnexions = []
    for i in indexConnexions:
        linesConnexions.append(uicLines[i])

    # suppression des connections
    for i in reversed(indexConnexions):
        del uicLines[i]

    # mise au propre du setting des proprietes des objets Python --------------

    # ne pas le descendre car risque d'avoir des problemes de tinySetProperties qui efface trucs crees pour slots
    # recherche tous les objet correspondant a des plugins python
    # PyObjsDict[PyObjName] = {'type' : Module , 'initArgsKeys' : initArgsKeys , 'initArgsValues' : initArgsValues }
    ##PyObjs = findPyObjs(uicLines)
    # tinySetProperty(uicLines,PyObjs)

    pluginInstancesDict = findPluginInstances(uicLines)
    tinySetItems(uicLines, pluginInstancesDict)
    tinySetProperties(uicLines, pluginInstancesDict)
    QtInstancesDict = findQtInstances(uicLines)
    tinySetProperties(uicLines, QtInstancesDict)

    # Analyse --------------------------------------

    # Analyse des connexion de facon crue
    connexionRaws = []
    for line in linesConnexions:
        connexionRaw = analyseOneConnexionRaw(line)
        connexionRaws.append(connexionRaw)

    # re-analyse pour faire la part entre connection entre 2 objet normaux  et celles correspondant a des input ou output

    connexionsNew = []
    dictInputSlots = dict()
    dictOutputSignals = dict()
    outputSignalsInInputSlot = []
    argumentsToAdd = dict()
    # propertiesToAdd  = dict()

    # hack pour determiner si un widget à été créer à partir d'un containeur .

    uiStr = read(path)
    containerStart = uiStr.find(" <widget class=") + 1 + len(" <widget class=")
    containerEnd = uiStr.find('"', containerStart)
    containerWidget = uiStr[containerStart:containerEnd]
    isHerited = containerWidget not in ["QWidget", "QMainWindow"]
    if not isHerited:
        containerWidget = "QtWidgets." + containerWidget
    else:
        classLineIndex = findLine(uicLines, "class Ui_")
        uicLines.insert(
            classLineIndex,
            "{containerWidget} = type('{containerWidget}', (QtWidgets.QWidget,), dict({containerWidget}.__dict__))".format(
                containerWidget=containerWidget
            ),
        )

    for connexionRaw in connexionRaws:
        sender, signal, signature, slot = connexionRaw

        # reconnais input et output ---------
        outputSignal = None
        if (
            designerParameters.useIntoTheVoidConnection
            and slot.startswith(widget)
            and not isHerited
        ):  # A REVOIR  ( comparaison pas robuste)      # traitement special pour connections dans vide
            slotName = slot.split(".")[1]
            # verifie que c'est pas un slot herite de QWidget et qu'il faut donc bien le transformer en signal de sortie du widget.
            if slotName not in [
                "close",
                "deleteLater",
                "hide",
                "lower",
                "raise",
                "repaint",
                "setDisabled",
                "setEnabled",
                "setFocus",
                "setHidden",
                "setStyleSheet",
                "virtual setVisible",
                "setWindowModified",
                "setWindowTitle",
                "show",
                "showFullScreen",
                "showMaximized",
                "showMinimized",
                "showNormal",
                "update",
            ]:
                outputSignal = slot.replace(classString, "self")

        inputSlot = None
        if (
            designerParameters.useIntoTheVoidConnection
            and sender.startswith(widget)
            and not isHerited
        ):  # A REVOIR  ( comparaison pas robuste)    # traitement special pour connections dans vide
            # verifie que c'est pas un signal herite de QWidget et qu'il faut donc bien le transformer en slot du widget.
            if signal not in ["customContextMenuRequested", "destroyed"]:
                inputSlot = signal

        # stock les in et out dans dictionnaire et stock evenutellemnt connections a recreer en newstyle --------------------
        if inputSlot:  # on a une entree
            # print('on a une entree connecte')
            # connectee direcement a sorti => doit creer un signal de sortie
            if outputSignal:
                # print('connecte directement a sortie')
                outputSignalsInInputSlot.append(
                    outputSignal
                )  # servira a faire la difference avec slot pour pouvoir emit dans la recostruciton des methodes pour slots du patch
                slot = outputSignal
                try:
                    dictOutputSignals[outputSignal].append(signature)
                except:
                    dictOutputSignals.update({outputSignal: [signature]})

            # conrespondant a un slot (connection dans vide ou objet inpute avec propriete 'signal' True)
            try:
                dictInputSlots[inputSlot][signature].append(slot)
            except:
                try:
                    dictInputSlots[inputSlot].update({signature: [slot]})
                except:
                    dictInputSlots.update({inputSlot: {signature: [slot]}})

        elif outputSignal:
            # print(outputSignal)
            try:
                dictOutputSignals[outputSignal].append(signature)
            except:
                dictOutputSignals.update({outputSignal: [signature]})
            if signature == "":
                signatureSignal = ""
            else:
                signatureSignal = "[" + signature + "]"
            connexionsNew.append(
                [sender, signal, signature, outputSignal + signatureSignal]
            )

        else:
            # correspond a une connexion normale entre 2 objet
            connexionsNew.append(connexionRaw)

    # creer les nouveau argument du __init__ , ne pas trop le descendre car rajoute du code a la fin qui doit etre fin du __init__
    arguments = ["parent = None"]
    initCodes = []
    if (
        argumentsToAdd
    ):  # pour l'instant c'est un dictionnaire vide, mais un jour on aura facon de definir un dictionnaire directement dans designer ?
        for name, [destinataire, value] in argumentsToAdd.items():
            value = eval(value)
            if value != "":
                arguments.append(name + "=" + value)
                initCodes.append(destinataire + "(" + name + ")")
    arguments.append("**kwargs")
    # print(widget)
    if initCodes:
        uicLines.extend(
            ["", "        # intialized by arguments"]
            + ["        " + initCode for initCode in initCodes]
        )

    # creer les nouvelles properties
    """
    codeToAdd = []
    for Key, destinataire in  propertiesToAdd.iteritmes : 
        codeToAdd.append('def set' + Key + '(self,value):\n'"    "+ destinataire + '(' + value + ')')       
        codeToAdd.append('def get' + Key + '(self):')
        if attributType == '_arg':
            codeToAdd.append("    return self._"+ key )       
        else:
            codeToAdd.append("    return self.__dict__['"+ key + "']")       
        codeToAdd.append(key+' = QtCore.Property(' + eval(value).__class__.__name__ + ', ' + getter +', '+ setter + ')')
    """

    # recree les connexions en newstyle pour les connextion normales et vers signal de sorite---------

    # print(connexionsNew)

    connexionsNew.sort()  # trie les connexions
    connexionLines = []
    for connexion in connexionsNew:
        [sender, signal, signature, slot] = connexion
        if signature != "":
            signature = "[" + signature + "]"
        connexionLines.append(
            "        " + sender + "." + signal + signature + ".connect(" + slot + ")"
        )
    if connexionLines:
        indexInsertConnexion = len(uicLines)
        inserts(
            uicLines,
            indexInsertConnexion,
            ["", "        # Connexions"] + connexionLines,
        )

    # deplacement et regroupement des setGeometry pour les objets graphiques ?

    uicLines.extend(["", "        # Graphics"])
    # moveLinesWithToEnd(uicLines,'Layout')      faut la merde en deplacant a la fin la creation d'objet dont il a besoin plus tot
    moveLinesWithToEnd(uicLines, "sizePolicy")
    moveLinesWithToEnd(uicLines, widget + ".resize(", sort=True, stopWithFirst=True)
    moveLinesWithToEnd(
        uicLines, [".setGeometry", ".setMinimumSize", ".setMaximumSize"], sort=True
    )

    # creation des signaux avec leurs surcharges (outputSignals)

    if dictOutputSignals:
        indexInsertSignals = len(uicLines)
        for outputSignal, signatures in dictOutputSignals.items():
            if len(signatures) > 1:
                signaturesStr = "[" + "][".join(signatures) + "]"
            else:
                signaturesStr = signatures[0]
            outputSignalWithoutSelf = outputSignal[5:]
            uicLines.insert(
                indexInsertSignals,
                "    "
                + outputSignalWithoutSelf
                + " = QtCore.Signal("
                + signaturesStr
                + ")",
            )
        inserts(uicLines, indexInsertSignals, ["", "    # signals", ""])

    # mise des connextion input -> objet directement sous forme de methode
    # detecte les surcharges, groupe les signatures qui pointent sur les meme slots ...
    # soit si toutes les signature d'une meme source pointent sur les meme slots....

    if dictInputSlots:
        uicLines.extend(["", "    # slots"])

        for inputSlot, signatureAndSlot in dictInputSlots.items():
            # Regroupe les signatures ayant les memes slots
            dictSlots = dict()
            for signature, slots in signatureAndSlot.items():
                slotsString = " ".join(slots)
                try:
                    dictSlots[slotsString].append(signature)
                except:
                    dictSlots.update({slotsString: [signature]})

            for slotsString, signatures in dictSlots.items():
                slots = slotsString.split(" ")
                uicLines.append("")
                for signature in signatures:
                    uicLines.append("    @QtCore.Slot(" + signature + ")")
                uicLines.append("    def " + inputSlot + "(self,value):")
                for slot in slots:
                    if slot in outputSignalsInInputSlot:
                        if signature != "" and len(dictOutputSignals[slot]) > 1:
                            signature = "[" + signature + "]"
                            uicLines.append(
                                "        " + slot + signature + ".emit(value)"
                            )
                        else:
                            uicLines.append("        " + slot + ".emit(value)")
                    else:
                        uicLines.append("        " + slot + "(value)")
                        # print('        '+ slot + '(value)')

    # replacement des 'widget', 'form' etc par self
    # on ne peut pas le faire pluto tot car on se sert de widget pour reconnaitre les connection a des slot dans vide
    # A REVOIR : remplacement hyper bourin !!!!!!
    replaceInLines(uicLines, widget + ".", "self.")
    replaceInLines(uicLines, "(" + widget, "(self")

    replaceLine(
        uicLines,
        "def setupUi(self,",
        [
            "",
            "    # constructor",
            "",
            "    def __init__(self," + ",".join(arguments) + "):",
            f"        super({containerWidget}, self).__init__(parent,**kwargs)",
            "",
        ],
    )

    # Ajouts, pour taille dans designer  ?
    # =>  je l'ai vire d'ici , maintenant rajoute la methode dynamiquement dans le plugin designer !!!
    # uicLines.append('\n    def sizeHint(self):\n        return self.size()\n')

    if findUI(uicLines):
        # si oui ajout de UI a la fin du nom de l'objet et heritage de QtWidgets.QWidget
        if widgetName[-2:] != "UI":
            widgetName = widgetName + "UI"
        widgetPyPath = joinPath(widgetDirectory, widgetName, "py")
        UI = True

    else:
        # sinon juste heritage de QtCore.QObject
        widgetPyPath = joinPath(widgetDirectory, widgetName, "py")
        UI = False

    # "%s/SmartRobotUI_%s.ini"%(os.path.dirname(__file__),platform.node())
    # Sauvegarde et restoration des position des Docks dans un fichier .ini
    if widget == "MainWindow":
        uicLines.insert(0, "import platform")
        uicLines.insert(0, "import os")
        uicLines.append(
            """ 
        # Restoration position des Docks
        settings = QSettings("%%s/%s_%%s.ini"%%(os.path.dirname(__file__),platform.node()), QSettings.IniFormat)
        if settings.value("geometry") is not None:
            self.restoreGeometry(settings.value("geometry"))
        if settings.value("windowState") is not None:
            self.restoreState(settings.value("windowState"))

    def closeEvent(self, event):
        # Sauvegardes position des Docks
        settings = QSettings("%%s/%s_%%s.ini"%%(os.path.dirname(__file__),platform.node()), QSettings.IniFormat)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        QtWidgets.QMainWindow.closeEvent(self, event)"""
            % (widgetName, widgetName)
        )

        if minimizeInSysTray:
            uicLines.append(
                '''
    def sysTrayIconActivated(self, reason):
        """https://stackoverflow.com/questions/34241202/python-pyqt-catch-minimize-event"""
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            if self.isHidden(): 
                self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized)
                self.show()
                self.activateWindow()
            else:
                self.hide()

    def changeEvent(self, event):
        """permet de cacher quand minimize pour ne laisser icone que dans system tray 
        https://stackoverflow.com/questions/34241202/python-pyqt-catch-minimize-event"""
        if(event.type() == QtCore.QEvent.WindowStateChange and self.isMinimized()):
            self.hide()
            event.accept()
            return
        QtWidgets.QMainWindow.changeEvent(self,event)'''
            )

    # version UI ? et ajout __main__ pour execution en stand alone  -----------------------------------------------------------
    WidgetName = widgetName[0].upper() + widgetName[1:]
    WidgetUI = WidgetName
    Widget = WidgetName.rstrip("UI")
    if UI:
        replaceLine(uicLines, "class Ui_", f"class {WidgetName}({containerWidget}):")
        # Ajout pour execution en stand alone du script
        if widget == "MainWindow":
            uicLines.append(
                f"""
if __name__ == "__main__":  
    import sys
    app = QtWidgets.QApplication(sys.argv)    
    widget = {WidgetUI}()
    widget.setWindowTitle(f"{Widget} ({{API_NAME}})") 
    widget.setTabPosition ( QtCore.Qt.AllDockWidgetAreas, QtWidgets.QTabWidget.North)
    widget.setDockOptions(widget.dockOptions()|widget.GroupedDragging)"""
            )
            if minimizeInSysTray:
                uicLines.append(
                    f"""     
    iconPath  = os.path.dirname(__file__)+"/{Widget}.ico"
    if os.path.exists(iconPath):
        icon = QtGui.QIcon(iconPath)
        widget.setWindowIcon(icon)
        systemTrayIcon = QtWidgets.QSystemTrayIcon(icon)
        systemTrayIcon.setIcon(icon)
        systemTrayIcon.show()
        systemTrayIcon.setToolTip("SmartRobot")
        systemTrayIcon.activated.connect(widget.sysTrayIconActivated)"""
                )
            else:
                uicLines.append(
                    f"""     
    iconPath  = os.path.dirname(__file__)+"/{Widget}.ico"
    if os.path.exists(iconPath):
        widget.setWindowIcon(QtGui.QIcon(iconPath))"""
                )
                if widgetName == "SmartFaceUI":
                    uicLines.append(
                        """
    for key,value in widget.__dict__.items():
        if isinstance(value,QtWidgets.QDockWidget):
            value.setTitleBarWidget(CustomTitleBar(parent = value))  
    if platform.node() == "SMARTOCTOPUS":
        widget.showFullScreen()
    else :         
        widget.show()"""
                    )
                else:
                    uicLines.append(
                        """
    widget.show()"""
                    )

            uicLines.append(
                """
    widget.window().activateWindow()
    app.exec_()
    del widget
    del app"""
            )

        else:
            uicLines.append(
                """
if __name__ == "__main__":  
    import sys
    app = QtWidgets.QApplication(sys.argv)      
    widget = """
                + WidgetName
                + f"""()
    widget.setWindowTitle(f"{Widget} ({{API_NAME}})") 
    widget.show()
    app.exec_()
    del widget
    del app"""
            )

    else:
        WidgetName = widgetName[0].upper() + widgetName[1:]
        replaceLine(uicLines, "class Ui_", "class " + WidgetName + "(QtCore.QObject):")
        delLine(uicLines, "        # geometry")
        delLine(
            uicLines, "        self.resize("
        )  # enleve en meme temps # geometry qui est dans la ligne (avec un "\n")

        # Ajout pour execution en stand alone du script
        uicLines.append(
            """
if __name__ == "__main__":  
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = """
            + WidgetName
            + """()
    app.exec_()
    del widget
    del app"""
        )

    # rajoute
    # uicLines.insert(0,'# coding: utf-8')

    # supressions finale :
    delLine(uicLines, "self.retranslateUi(")

    delLines(
        uicLines, ".setObjectName("
    )  # le met à la fin pour pouvoir transformet setObjectName en argument du init d'un objet, si on l'a rajouté comme argument, par exemple pour l'objet SmartPlotUI, affin qu'il puisse connaitre son nom et reconnaitre qu'un plot lui est destiné

    # ajoute deux fonctions pour aguster automatiquement QtCore.QSize et QtCore.QRect à la résolution de l'ecran  ---------------------------------------------------
    addScaledImport = False
    for i, line in enumerate(uicLines):
        for resizable in ("QtCore.QSize(", "QtCore.QRect("):
            start = line.find(resizable)
            while start != -1:
                # print(start)
                addScaledImport = True
                end = line.find(")", start)
                line = line[:start] + "scaled(" + line[start:end] + ")" + line[end:]
                uicLines[i] = line
                start = line.find(resizable, end + 7)

        for argsResizable in ("setContentsMargins(", "spacing="):
            start = line.find(argsResizable)
            if start != -1:
                start = start + len(argsResizable)
                if argsResizable[-1] == "(":
                    end = line.find(")", start)
                else:
                    for end in range(start, len(line)):
                        if line[end] not in "0123456789.":
                            break
                content = line[start:end]
                if content.find(",") != -1:
                    if content != "0, 0, 0, 0":
                        addScaledImport = True
                        uicLines[i] = (
                            line[:start]
                            + "*scaled("
                            + line[start:end]
                            + ")"
                            + line[end:]
                        )
                else:
                    if content != "0":
                        addScaledImport = True
                        uicLines[i] = (
                            line[:start]
                            + "scaled("
                            + line[start:end]
                            + ")"
                            + line[end:]
                        )

    addImport = [
        "from SmartFramework.ui import exceptionDialog,CustomTitleBar",
        "from qtpy.QtCore import QSettings",
    ]

    if addScaledImport:
        reversedImportLines[-1] += ", scaled"

    for importLine in addImport + reversedImportLines:
        uicLines.insert(0, importLine)

    # fait
    # ecriture du fichier s
    string = "\n".join(removeDoubleNewLine(uicLines))
    black_string = black.format_str(string, mode=black.Mode(line_length=88))
    write(widgetPyPath, black_string)
    # write(widgetPyPath, removeDoubleNewLine(uicLines), newline="\r\n")

    return widgetPyPath

    # generation du fichier WidgetPlugin.py pour Qt Designer
    # generation du fichier sans object UI si y'en avait et que peut les remplacer par des objets non UI
    # generation du fichier DI si existe version sans UI


if __name__ == "__main__":
    import sys
    import os
    from SmartFramework.files import cleanDropNames

    # print(sys.argv)
    cleanDropNames(sys.argv)
    # print(sys.argv)
    # sys.argv = ["", "D:/Projets/Python/SmartRobot/SmartRobot.ui"]
    # sys.argv = ["", "D:/Projets/Python/SmartFace/patchs/SmartFace.ui"]
    # sys.argv = ["", "/media/DATA/Python/SmartFace/patchs/SmartFaceEdit.ui"]
    # sys.argv = ["", "D:/Projets/Python/SmartFace/patchs/SmartFaceRecord.ui"]
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        paths = (
            chercheExt("D:/Projets/Python/SmartFace", "ui")
            + chercheExt("D:/Projets/Python/SmartFace/patchs", "ui")
            + chercheExt("D:/Projets/Python/SmartFramework/video", "ui")
        )
    # paths = ["D:/Documents/Bureau/untitled.ui"]
    for path in paths:
        print(path)
        try:
            uiToPython(path)
        # os.system("pause")
        except:
            exc_info = sys.exc_info()
            print(exc_info[1])
            import traceback

            print(traceback.format_exc())
            # print(traceback.format_exc(exc_info[2]))
            os.system("pause")
