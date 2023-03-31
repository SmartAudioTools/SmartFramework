# -*- coding: utf-8 -*-
import os
from SmartFramework.designer import (
    findLine,
    findObjectEnd,
    findUI,
    replaceInLines,
    delLines,
)
from SmartFramework.files import write, splitPath, readLines

ascIfWarning = True


def pywToPy(path):

    # designerDirectory = directory(__file__)
    folder, name, extension = splitPath(path)

    # ouverture du fichier py
    Name = name[0].upper() + name[1:]
    moduleStrListe = readLines(path)

    # verifie que le nom du module commence par une Majuscule
    WARNING = 0
    if name[0].islower():
        print(
            "WARNING: le fichier contenant l'objets PyQt destinés à être compilés doit commencer par une Majuscule"
        )
        WARNING = 1

    # recher la classe qui a le meme nom que le module avec premiere lettre capitalisee
    indexClass = findLine(moduleStrListe, "class " + Name + "(")
    if indexClass == -1:
        print(
            "ERREURE : ne trouve pas la classe du meme Nom que le module (avec premiere lettre capitalisee)"
        )
        os.system("pause")
        return 0

    # recupère code de la classe
    lineClass = moduleStrListe[indexClass]
    heritageStart = lineClass.find("(", 1)
    heritageEnd = lineClass.rfind(")", 1)
    heritageListe = lineClass[heritageStart + 1 : heritageEnd].split(",")
    indexClassEnd = findObjectEnd(moduleStrListe, Name)

    # regarde si la classe contient des objets graphiques (attribut ou heritage)
    presenceAttributesUI = findUI(moduleStrListe[indexClass + 1 : indexClassEnd])
    presenceHeritageUI = (findLine(heritageListe, "QtGui") != -1) or (
        findLine(heritageListe, "UI") != -1
    )

    # si y'a des attributs ou heritage graphique
    if (
        presenceAttributesUI
        or presenceHeritageUI
        or Name[-2:] == "UI"
        or extension == "pyw"
    ):
        # print('findUI')

        if not presenceAttributesUI:
            print("WARNING : UI class contain not UI attributes ")
            WARNING = 1

        if extension != "pyw":
            print("WARNING : UI module should have the 'pyw' extension")
            WARNING = 1
        if Name[-2:] != "UI":
            print("WARNING : UI module and Class name should finish by 'UI'")
            WARNING = 1

        if findLine(heritageListe, "QtCore") != -1:
            print(
                "ERREURE : Class containing UI objects should'nt herite from QtCore objects"
            )
            os.system("pause")
            return 0

        if WARNING and ascIfWarning:
            while True:
                input = input("Do you want to continue(Y/N)? ").lower()
                if input == "y":
                    break
                elif input == "n":
                    return 0

        # Genere une version sans UI ?
        if (
            findLine(moduleStrListe[indexClass + 1 : indexClassEnd], " = QtWidgets.")
            == -1
        ):
            # les object graphiques finissent tous par UI (ne sont pas directement des objet QtWidgets.)
            # => peut generer une version non graphique ?

            # verifie que le fichier n'existe pas déjà ....
            moduleWithoutUIPath = os.path.join(folder, name[:-2] + ".py")

            """
            if os.path.exists(moduleWithoutUIPath):
                    while True :
                    input= raw_input("No-UI version already existe. Override (Y/N)? ").lower()
                    if input  == 'y':
                        break
                    elif input== 'n':
                        return 0
            """

            # remplace les objets UI par des version non UI. (devrait verifier que la version non UI existe ... mais c'est compliqué)
            replaceInLines(moduleStrListe, "UI", "")
            replaceInLines(moduleStrListe, "QtWidgets.QWidget", "QtCore.QObject")
            delLines(moduleStrListe, ".setGeometry")
            delLines(moduleStrListe, ".resize")

            # suprime la ligne widget.show() dans le main si pas dans close try:
            lineShow = findLine(moduleStrListe, "widget.show()")
            if lineShow != -1 and moduleStrListe[lineShow - 1].find("try") == -1:
                del moduleStrListe[lineShow]

            # créer le fichier
            write(
                moduleWithoutUIPath, moduleStrListe, encoding="utf-8", newline="\n"
            )
            # pythonToQtDesigner(moduleWithoutUIPath)
            return moduleWithoutUIPath
        else:
            print(
                "Impossible de creer version non-graphique car l'objet contient des objets graphiques Qt sans version non-graphique"
            )
            os.system("pause")
            return 0
    else:
        print("l'objet ne semble pas être un objet graphique")
        return 0


if __name__ == "__main__":
    import sys

    path = sys.argv[1]
    # directory, filename , extension = splitPath(path)
    try:
        pywToPy(path)
    except:
        print(sys.exc_info()[1])
        os.system("pause")
