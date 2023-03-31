def checkPaths(obj):
    ok = True
    if type(obj) == dict:
        for value in obj.values():
            if not checkPaths(value):
                ok = False
    elif type(obj) == list:
        for value in obj:
            if not checkPaths(value):
                ok = False
    elif isinstance(obj, str):
        if (obj.find("/") != -1 or obj.find("\\") != -1) and not os.path.exists(obj):
            print("\n " + obj + " n'est pas un chemin valide", end=" ")
            ok = False
    return ok


try:
    import sys
    import os
    from SmartFramework.serialize import serializejsonlab
    from SmartFramework.files import name, ext, cleanDropNames

    cleanDropNames(sys.argv)
    jsonPaths = [path for path in sys.argv[1:] if ext(path) == "json"]
    for jsonPath in jsonPaths:
        print(name(jsonPath) + ": ", end=" ")
        json = serializejsonlab.load(jsonPath)
        if checkPaths(json):
            print("OK !")
        else:
            print("\n")
    print("\n")
    os.system("pause")

except:
    import traceback

    traceback.print_exc()
    print("\n")
    os.system("pause")
