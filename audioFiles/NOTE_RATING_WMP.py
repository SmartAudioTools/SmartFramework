from SmartFramework.files import dragAndDrop, changeExt, directory
import os
import sys
from SmartFramework.audioFiles.infos import saveStars
import mutagen

os.chdir(directory(sys.argv[0]))

RATING_TO_RATING_WMP = {"1": "51", "25": "102", "50": "153", "75": "204", "99": "255"}


def callback(path):
    asf = mutagen.flac.FLAC(path)
    if "RATING" in asf:
        asf["RATING WMP"] = RATING_TO_RATING_WMP[asf["RATING"][0]]
        # del(asf["RATING WMP"] )
        asf.save()


dragAndDrop(callback=callback, extension=["flac"], recursive=True)
