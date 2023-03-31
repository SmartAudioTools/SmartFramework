from SmartFramework.files import dragAndDrop, changeExt, directory
import os
import sys

os.chdir(directory(sys.argv[0]))


def callback(path):
    mp3Path = changeExt(path, "mp3")
    if not os.path.exists(mp3Path):
        commande = 'ffmpeg.exe -i "' + path + '" -vn -ab 156k "' + mp3Path + '"'
        os.system(commande)


dragAndDrop(
    callback=callback,
    extension=["avi", "mkv", "mp4", "webm", "m4a", "flac"],
    processes=1,
)
