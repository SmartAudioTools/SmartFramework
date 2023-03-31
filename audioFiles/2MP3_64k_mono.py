from SmartFramework.files import dragAndDrop, changeExt, directory
import os
import sys

os.chdir(directory(sys.argv[0]))


def callback(path):
    mp3Path = changeExt(path, "mp3")
    if not os.path.exists(mp3Path):
        commande = (
            'ffmpeg.exe -i "' + path + '" -vn -ab 64k -ac 1 "' + mp3Path + '"'
        )  # -filter:a "highpass=f=40, volume=25dB"
        os.system(commande)


if __name__ == "__main__":
    dragAndDrop(
        callback=callback,
        extension=["avi", "mkv", "mp4", "webm", "m4a", "flac", "wav", "mpg"],
        processes=8,
    )
