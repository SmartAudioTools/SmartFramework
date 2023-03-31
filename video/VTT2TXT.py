# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 22:07:00 2018

@author: Baptiste
"""
from SmartFramework.files import dragAndDrop, changeExt, readLines, writeLines  # ,name

# sys.argv = ["", "D:/Documents/Bureau/Nouveau dossier (2)"]


def callback(path):
    lines = readLines(path)
    newlines = []
    count = 1
    for line in lines[4:]:
        line = line.strip()
        if line:
            if line.find("-->") != -1:
                line = line.replace(" align:start position:0%", "").replace(".", ",")
                newlines.append("\n\n" + str(count) + "\n" + line)
                count += 1
            else:
                newlist = []
                skip = False
                if line[0] == "-":
                    newlist.append("\n")
                else:
                    newlist.append(" ")
                for c in line:
                    if c == "<":
                        skip = True
                    elif c == ">":
                        skip = False
                    elif not skip:
                        newlist.append(c)
                newline = "".join(newlist).strip()
                newlines.append(newline)
    newPath = changeExt(path, "srt")
    writeLines(newPath, newlines)
    # newFile.write("\n".join(newlines).replace("\n\n\n","\n\n").replace("\n\n\n","\n\n"))


dragAndDrop(callback=callback, extension="vtt")
