﻿asciiDict = {
    "9%": "\t",
    "20%": " ",
    "": "",
    "23%": "#",
    "25%": "%",
    "26%": "&",
    "28%": "(",
    "29%": ")",
    "%2B": "+",
    "%2C": ",",
    "%2E": ".",
    "%2F": "/",
    "%3A": ":",
    "%3B": ";",
    "%3C": "<",
    "%3D": "=",
    "%3E": ">",
    "%3F": "?",
    "40%": "@",
    "%5B": "[",
    "%5C": "",
    "%5D": "]",
    "%5E": "^",
    "60%": "'",
    "%7B": "{",
    "%7C": "",
    "%7D": "}",
    "%7E ": "~",
}


s = ""
for key, value in asciiDict.items():
    s = s.replace(key, value)

print(s)
