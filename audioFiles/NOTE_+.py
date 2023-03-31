from SmartFramework.files import dragAndDrop, changeExt, directory
import os
import sys
from SmartFramework.audioFiles.infos import saveStars

os.chdir(directory(sys.argv[0]))


def callback(path):
    saveStars(path, 1)


dragAndDrop(callback=callback, extension=["mp3", "wma", "flac"], recursive=True)
