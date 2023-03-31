# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 20:09:11 2017

@author: Baptiste
"""


import pip._internal

pip._internal.main(["install", "yt_dlp", "--upgrade"])
import yt_dlp as youtube_dl
import os
import parse
from SmartFramework.web import htmlFromUrl

# rajoute le dossier contenant ffmpeg.exe et ffprobe.exe
os.environ["PATH"] = os.environ["PATH"] + ";" + os.path.dirname(__file__)


def youtubeToMp3(link, pathTemplate="%(title)s.%(ext)s"):
    if link.find("soundcloud") != -1:
        html = htmlFromUrl(link)
        try:
            artist = parse.search('"artist":"{}",', html)[0]
        except:
            artist = parse.search('"username":"{}",', html)[0]
        pathTemplate = pathTemplate.replace(
            "%(title)s", "{} - %(title)s".format(artist)
        )
    ydl_opts = {
        "outtmpl": pathTemplate,
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "256",
            }
        ],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


if __name__ == "__main__":
    links = [
        "https://www.youtube.com/watch?v=ABIbH-LtpFs",
        "https://www.youtube.com/watch?v=FrEP4MHCKDc"
    ]
    for link in links:
        youtubeToMp3(link)
