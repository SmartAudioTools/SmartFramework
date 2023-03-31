# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 12:35:30 2020

@author: Baptiste
"""
from chardet import UniversalDetector

detector = UniversalDetector()
text = """salut ! j'ai bien mangé"""


for line in text.splitlines():
    # print(line)
    detector.feed(line.encode("utf8"))
    if detector.done:
        print("break")
        break
print(detector.done)
detector.close()
print(detector.result)
