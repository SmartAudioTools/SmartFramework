# -*- coding: utf-8 -*-
"""
https://stackoverflow.com/questions/580924/python-windows-file-version-attribute
"""


import win32api


def getProperty(path, propertyName):
    """
    Read properties of the given file
    'Comments', 'InternalName', 'ProductName',
    'CompanyName', 'LegalCopyright', 'ProductVersion',
    'FileDescription', 'LegalTrademarks', 'PrivateBuild',
    'FileVersion', 'OriginalFilename', 'SpecialBuild')
    """
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation"
        )[0]
        strInfoPath = "\\StringFileInfo\\%04X%04X\\%s" % (lang, codepage, propertyName)
        return win32api.GetFileVersionInfo(path, strInfoPath)
    except:
        return None


def getComment(path):
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation"
        )[0]
        strInfoPath = "\\StringFileInfo\\%04X%04X\\%s" % (lang, codepage, "Comments")
        return win32api.GetFileVersionInfo(path, strInfoPath)
    except:
        return None


def getDescription(path):
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation"
        )[0]
        strInfoPath = "\\StringFileInfo\\%04X%04X\\%s" % (
            lang,
            codepage,
            "FileDescription",
        )
        return win32api.GetFileVersionInfo(path, strInfoPath)
    except:
        return None


properties = getDescription("C:/Program Files/Windows NT/Accessories/wordpad.exe")
print(properties)
