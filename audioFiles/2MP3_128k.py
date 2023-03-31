try:
    import sys
    import os
    import subprocess
    from SmartFramework.files import cleanDropNames, directory, changeExt

    cleanDropNames(sys.argv)
    os.chdir(directory(sys.argv[0]))

    # sys.argv = ['',"D:/Documents/Bureau/Nouveau dossier/VOICE/IM - 111008-205735.WAV"]
    if len(sys.argv) > 1:
        moviesPaths = sys.argv[1:]
        for moviesPath in moviesPaths:
            # commande = 'ffmpeg.exe -i "' + moviesPath + '" -vn -acodec copy "' + changeExt(moviesPath,'aac') + '"'
            commande = (
                'ffmpeg.exe -i "'
                + moviesPath
                + '" -vn -ab 128k "'
                + changeExt(moviesPath, "mp3")
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
