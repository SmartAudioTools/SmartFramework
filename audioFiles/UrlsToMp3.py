# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 22:14:08 2019

@author: Baptiste
"""
from SmartFramework.web import htmlFromUrl, extractVideoAndAudioUrls
from SmartFramework.audioFiles.youtubeToMp3 import youtubeToMp3
from SmartFramework.serialize import serializejson
import os

urls = [
    "https://www.indiemusic.fr/crossroads-festival-2019/",
    "https://www.indiemusic.fr/crossroads-festival-2019/2/",
    "https://www.indiemusic.fr/crossroads-festival-2019/3/",
    "https://www.indiemusic.fr/crossroads-festival-2019/4/",
    "https://www.indiemusic.fr/crossroads-festival-2019/5/",
    "https://www.indiemusic.fr/crossroads-festival-2019/6/",
    "https://www.indiemusic.fr/crossroads-festival-2019/7/",
    "https://www.indiemusic.fr/crossroads-festival-2019/8/",
    "https://www.indiemusic.fr/crossroads-festival-2018-presentation/",
    "https://www.indiemusic.fr/crossroads-festival-2018-presentation/2/",
    "https://www.indiemusic.fr/crossroads-festival-2018-presentation/3/",
    "https://www.indiemusic.fr/crossroads-festival-2018-presentation/4/",
    "https://www.indiemusic.fr/crossroads-festival-2018-presentation/5/",
    "https://www.indiemusic.fr/crossroads-festival-2018-presentation/6/",
    "https://www.indiemusic.fr/crossroads-festival-2018-presentation/7/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/2/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/3/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/4/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/5/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/6/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/7/",
    "https://www.indiemusic.fr/crossroads-festival-2017-presentation/8/",
    "https://www.indiemusic.fr/crossroads-festival-2016/",
]
allVideos = []
for url in urls:
    print(url)
    html = htmlFromUrl(url)
    videos = extractVideoAndAudioUrls(html)
    allVideos.extend(videos)

downloadedPath = "downloaded.json"
if os.path.exists(downloadedPath):
    downloaded = serializejson.load(downloadedPath)
else:
    print("impossible de trouver %s" % downloadedPath)
    downloaded = []
# print(allVideos)
for video in allVideos:
    if video not in downloaded:
        try:
            youtubeToMp3(video, "%(title)s.%(ext)s")
            downloaded.append(video)
            serializejson.dump(downloaded, downloadedPath)
        except:
            print("impossible de telecharger %s" % video)
