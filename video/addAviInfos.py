from SmartFramework.files import dragAndDrop, addToName, joinPath, directory
import sys

# from SmartFramework.video.VideoInfos import VideoInfos
import os

# from hachoir.parser import createParser
# from hachoir.metadata import extractMetadata
# from hachoir.core.tools import makeUnicode
from hachoir.metadata import config
from shutil import move
import subprocess

# permet d'eviter de tronc la chaine de caractère contenant le json

config.MAX_STR_LENGTH = 0

# import sys
# sys.argv = ["", "D:/Dropbox/Smart Audio Tools/VIDEOS/Baptiste_DeLaGorce_Expressions"]
# from SmartFace.faceEditorTools import parseVideoName
# from SmartFramework.files import name
from simplejson import dumps
from SmartFramework.video.VideoInfos import VideoInfos


def callback(videoPath):
    infos = VideoInfos(videoPath, forcePathParsing=False)
    # result = parse("{firstName}_{lastName}_d={distance}_x={x}_y={y}_{expressions}", name(videoPath))
    # VideoInfos(result.named)
    tempPath = addToName(videoPath, "_")
    tags = {
        "comment": dumps(
            {
                "firstName": infos.firstName,
                "lastName": infos.lastName,
                "whiteMarkers": infos.whiteMarkers,
                "targets": infos.targets,
                "distance": infos.distance,
                "x": infos.x,
                "y": infos.y,
                "expressions": infos.expressions,
                "comment": infos.comment,
                "deviceId": "SmartCam[ikk166T7Oy8e0E4thOO7Q]",
                "mode": "BAYER",
                "resolution": infos.resolution,
                "gain": infos.gain,  # cv::CAP_PROP_GAIN =14,
                "exposure": infos.exposure,  # cv::CAP_PROP_EXPOSURE =15,
                "fps": infos.fps,  # cv::CAP_PROP_FPS =5,
                "diffuseur": infos.diffuseur,
                "plexi": infos.diffuseur,
                "filter": 850,
                "objectif": "PT-0412-SP1",
                "whiteBalance": infos.whiteBalance,
                "rotation": infos.rotation
                #  cv::CAP_PROP_WHITE_BALANCE_BLUE_U =17,  cv::CAP_PROP_WHITE_BALANCE_RED_V =26,
            }
        )
    }
    tagStrs = []
    for key, value in tags.items():
        tagStrs.append("%s=%s" % (key, value))
    args = (
        [joinPath(directory(__file__), "ffmpeg.exe"), "-i", videoPath, "-metadata"]
        + tagStrs
        + ["-codec", "copy", tempPath]
    )
    subprocess.call(args)
    move(tempPath, videoPath)


# import sys
# sys.argv = ["" , "D:/Dropbox/Smart Audio Tools/VIDEOS/Baptiste_DeLaGorce_Tests/2018/Pb Bouche/Nouveau dossier/Baptiste_DeLaGorce_2018-09-26_11H41_01.avi"]
dragAndDrop(callback=callback, extension="avi")
os.system("pause")
