# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 10:51:17 2020

@author: Baptiste
"""

import cchardet
import chardet

bytes_ = b"allm\xc3\xa4hlich"
bytes_ = open(
    "d:/projets/python/smartframework/string/dictionnaires/lexique_de.txt", "rb"
)

for ch in (cchardet, chardet):
    print(ch.__name__, "--------------")
    detector = ch.UniversalDetector()
    for i, bytes_line in enumerate(bytes_):
        detector.feed(bytes_line)
        if detector.done:
            print(i)
            break
    print(detector.done)
    detector.close()
    print(detector.result)


# rawBytes = open("d:/projets/python/smartframework/string/dictionnaires/lexique_de.txt","rb").read()
