from SmartFramework.designer.uiToPython import uiToPython

if __name__ == "__main__":
    import sys
    import os
    from SmartFramework.files import cleanDropNames

    cleanDropNames(sys.argv)
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
        # paths = ["D:/Documents/Bureau/untitled.ui"]
        for path in paths:
            print(path)
            # try:
            uiToPython(path, minimizeInSysTray=True)
            # os.system("pause")
            # except :
            ##    print(sys.exc_info()[1])
            #   #mport traceback
            # print(traceback.format_exc(sys.exc_info()[2]))
    else:
        print("drag'n'drop ui file on script")
    os.system("pause")
