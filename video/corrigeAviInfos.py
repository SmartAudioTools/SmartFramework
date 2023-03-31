from SmartFramework.files import dragAndDrop, addToName, joinPath, directory

# from SmartFramework.video.VideoInfos import VideoInfos
import os
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# from hachoir.core.tools import makeUnicode
from hachoir.metadata import config
from shutil import move
import subprocess

# permet d'eviter de tronc la chaine de caractère contenant le json
config.MAX_STR_LENGTH = 0

# import sys
# sys.argv = ["", "D:/Dropbox/Smart Audio Tools/VIDEOS/Baptiste_DeLaGorce_Expressions"]
oldToNew = {"Delagorce": "DeLaGorce"}


def callback(videoPath):
    parser = createParser(videoPath)
    metadata = extractMetadata(parser)
    commentItem = metadata.getItem("comment", 1)
    jsonStr = commentItem.value
    for old, new in oldToNew.items():
        jsonStr = jsonStr.replace(old, new)
    tempPath = addToName(videoPath, "_")
    tagStr = "comment=" + jsonStr
    args = [
        joinPath(directory(__file__), "ffmpeg.exe"),
        "-i",
        videoPath,
        "-metadata",
        tagStr,
        "-codec",
        "copy",
        tempPath,
    ]
    subprocess.call(args)
    move(tempPath, videoPath)


dragAndDrop(callback=callback, extension="avi")
os.system("pause")
