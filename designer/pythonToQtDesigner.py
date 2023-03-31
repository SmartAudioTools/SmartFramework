try:
    from SmartFramework.designer import (
        findLine,
        pythonToPlugin,
    )
    from SmartFramework.files import (
        splitPath,
        joinPath,
        chercheExt,
        directory,
        readLines,
        name,
    )
    import os
    import itertools

    # PYTHONPATH = "D:/Projets/Python"
    ascIfWarning = True

    def pythonToQtDesigner(path):
        # __file__ = 'D:/Projets/Python/Scripts/SmartFramework/SmartFramework_1_23/SmartFramework/ui/__init__.py'
        designerDirectory, fileName = os.path.split(__file__)
        directory, name, extension = splitPath(path)
        directory = directory.replace("\\", "/")
        # designerGroup = directory.replace(designerParameters.base_repertory, "")

        # ouverture du fichier py
        Name = name[0].upper() + name[1:]
        moduleStrListe = readLines(path, iterator=False)

        # verifie que le nom du module commence par une Majuscule
        if name[0].islower():
            print(
                "WARNING: le fichier contenant l'objets PyQt destinés à être compilés doit commencer par une Majuscule"
            )

        # recher la classe qui a le meme nom que le module avec premiere lettre capitalisee
        indexClassDefinitionStart = findLine(moduleStrListe, "class " + Name + "(")
        if indexClassDefinitionStart == -1:
            print(
                "ERREURE : ne trouve pas la classe du meme Nom que le module (avec premiere lettre capitalisee) %s"
                % Name
            )
            os.system("pause")
            return 0

        # si y'a des attributs ou heritage graphique
        if True:  # presenceAttributesUI or presenceHeritageUI or Name[-2:] == "UI":
            # print('findUI')

            # if not presenceAttributesUI and not presenceHeritageUI:
            ##    print(
            #       "WARNING : UI class contain not UI attributs and not herite from UI object "
            #    )
            #     WARNING = 1

            if extension != "pyw":
                print("WARNING : UI module should have the 'pyw' extension")
            if Name[-2:] != "UI":
                print("WARNING : UI module and Class name should finish by 'UI'")

        pythonToPlugin(path)

    if __name__ == "__main__":
        import sys
        from SmartFramework.files import cleanDropNames

        cleanDropNames(sys.argv)
        # sys.argv = ["", "D:/Projets/Python/SmartFramework/plot/PlotUI.pyw"]
        # sys.argv = [
        #    "",
        #    "D:\Projets\Python\SmartFramework\serialize/SerializePresetUI.pyw",
        # ]
        if len(sys.argv) > 1:
            path = sys.argv[1]
            pythonToPlugin(path)
            os.system("pause")

        else:
            pluginPaths = chercheExt(joinPath(directory(__file__), "plugins"), "py")
            for pluginPath in pluginPaths:
                plugin_name = name(pluginPath)
                if plugin_name.startswith("register"):
                    # if plugin_name.endswith("plugin"):
                    # pluginLines = readLines(pluginPath, iterator=False)
                    # returnLine = pluginLines[
                    #    findLine(pluginLines, "def includeFile(self):") + 1
                    # ]
                    # module = returnLine.split('"')[1]
                    # pathEnd = module.replace(".", "/")
                    pathEnd = name(pluginPath)[9:].replace("~", "/")
                    for folder, ext in itertools.product(sys.path, ("pyw", "py")):
                        pathTest = joinPath(folder, pathEnd, ext)
                        if os.path.exists(pathTest):
                            print(pathTest)
                            pythonToPlugin(pathTest)
                            break
                    else:
                        print(
                            "impossible de trouver le fichier correspondant à %s"
                            % pluginPath
                        )

            # return "SmartFramework.plot.CurveSelectorUI"
            # path = 'D:/Projets/Python/SmartFace/FaceControlSelect.py'
            # path = 'D:/Projets/Python/SmartFramework/files/FileSelectorUI.pyw'
except:
    import sys
    import os
    import traceback

    print(sys.exc_info()[1])
    print(traceback.format_exc())
    os.system("pause")
