# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 20:58:08 2021

@author: Baptiste
"""


separator = b"\xff\xd8\xff\xe0"
i = 0
path = "D:/Projets/~DMX/Thumbs.db"
with open(path, "rb") as content_file:
    content = content_file.read()
    thumbs = content.split(separator)
    for thumb in thumbs:
        i += 1
        print(i, path)
        output = open("D:/Projets/~DMX/%05i.jpg" % i, "wb")
        output.write(separator + thumb)
        output.close()
    content_file.close()
