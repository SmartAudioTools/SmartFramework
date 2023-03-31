try:
    import sys
    import os
    import subprocess
    from SmartFramework.files import cleanDropNames, directory, changeExt, addToName

    cleanDropNames(sys.argv)
    os.chdir(directory(sys.argv[0]))

    sys.argv = ["", "D:/Documents/Bureau/Nouveau dossier/20220208_124003.mp4"]
    if len(sys.argv) > 1:
        moviesPaths = sys.argv[1:]
        for moviesPath in moviesPaths:
            # commande = 'ffmpeg.exe -i "' + moviesPath + '" -vn -acodec copy "' + changeExt(moviesPath,'aac') + '"'
            commande = (
                'ffmpeg.exe -i "'
                + moviesPath
                + '" -vcodec libx265 -crf 28 "'
                + addToName(moviesPath, "_")
                + '"'
            )
            # commande = ['ffmpeg.exe','-i',moviesPath.,'-vn',u'-ab',u'360k',changeExt(moviesPath,'mp3')]
            # subprocess.call(commande)
            os.system(commande)
    else:
        print((sys.argv))
        print("il faut glisser les videos sur 2MP3.py")
        os.system("pause")

except:
    import traceback

    # print("erreure avec le fichier : %s" % jsonPath)
    traceback.print_exc()
    import os

    os.system("pause")
