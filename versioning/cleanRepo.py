# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 14:58:46 2018

@author: Baptiste
"""
from mercurial import ui, hg
from SmartFramework.files import (
    ext,
    cherche,
    directories,
    cleanPath,
    fileName,
    writeLines,
)
import os


if True:
    repoPath = "D:/Projets/Python/SmartFramework"
    excludeFileNames = set(["Deftones-Change.mp3", "downloaded.json"])
    excludeFolderNames = set(
        [
            "PyAudio",
            "faceTracker",
            "others",
            "dlls",
            "test_PNG",
            "icones",
            "Test new headers",
        ]
    )
    excludeExtensions = set(["pyc"])
    excludeExtensionsIfFileNotInLast = set(
        ["exe", "imbin", "dll", "txt", "json", "png"]
    )


elif False:
    repoPath = "D:/Projets/Python/SmartFace"
    excludeFileNames = set(
        ["SmartFaceEditUI.dat", "vc_redist.x64.exe", "vc_redist.x86.exe"]
    )
    excludeFolderNames = set(
        [
            "Test cropping",
            "Test new headers",
            "C#",
            "Debug",
            "Old",
            "old",
            ".vs",
            "jsonVisu",
            "Win32",
            "x64",
            "ipch",
            "videos",
            "irisTrackingPng",
            "Archive",
            "Assets",
            "ignore",
            "Docs",
            "Dropbox",
            "Samples",
            "Demo",
            "Sample",
        ]
    )
    excludeExtensions = set(
        [
            "pyc",
            "ncb",
            "ma",
            "sdf",
            "pdb",
            "log",
            "tlog",
            "suo",
            "obj",
            "avi",
            "user",
            "jpg",
            "mat",
            "msi",
            "imbin",
            "orig",
            "ini",
            "pkl",
            "manifest",
            "pdb",
            "obj",
            "lib",
            "db",
            "idb",
            "tst",
            "exp",
            "dep",
            "htm",
            "zip",
            "dll-efac4574",
            "dll-b3a51d95-fe898827",
            "dll-b3a51d95",
            "dll-ec6bb5c4",
            "npy",
            "bmp",
            "exe-f6db3396",
            "dll-87b9bc04",
            "dll-228c4f01",
            "bak",
            "exe-05bcc086-d5ef7de6",
            "exe-05bcc086",
            "exe-c5f7f152",
            "exe-a6f55ce2",
            "dll-ac459a97",
            "dae",
            "mb",
            "mesh",
            "doc",
            "js",
            "xls",
            "pdnsave",
            "pdn",
            "dsp",
            "ply",
            "pickle",
            "clw",
        ]
    )
    excludeExtensionsIfFileNotInLast = set(
        ["exe", "json", "dll", "dat", "png", "sync", "pdf", "xml", "rtf", "ico", "svg"]
    )


elif False:
    repoPath = "D:/Projets/Python/SmartTime"
    excludeFileNames = set(
        [
            "filesNameToPath.json",
            "ElapsedTime - Copie.json",
            "ElapsedTime avant 2017-01-09.json",
            "ElapsedTime avant 2019-07-30.json",
            "ElapsedTime.json",
        ]
    )
    excludeFolderNames = set(["dictionnaires"])
    excludeExtensions = set(["pyc", "icl"])
    excludeExtensionsIfFileNotInLast = set([])


elif False:
    repoPath = "D:/Projets/Python/SmartMusic"
    excludeFileNames = set(["geckodriver.log", "ffmpeg.exe", "geckodriver.exe"])
    excludeFolderNames = set(["old"])
    excludeExtensions = set(["pyc"])
    excludeExtensionsIfFileNotInLast = set(["json", "exe"])


elif False:
    repoPath = "D:/Projets/Python/SmartMovies"
    excludeFileNames = set([])
    excludeFolderNames = set(["2AVI", "old"])
    excludeExtensions = set(["pyc"])
    excludeExtensionsIfFileNotInLast = set(["json", "exe", "dat"])

u = ui.ui()
repo = hg.repository(u, repoPath.encode("cp1250"))


def getRepoActualFileInfos(repoPath):
    paths = cherche(repoPath, excludeFolders=[".hg"], recursive=True)
    pathMaxSize = dict()
    extensionMaxSize = dict()
    extensionPaths = dict()
    for path in paths:
        fileSize = os.path.getsize(path)
        pathMaxSize[path] = fileSize
        extension = ext(path)
        if extension not in extensionPaths:
            extensionPaths[extension] = set()
        extensionPaths[extension].add(path)
        if extension in extensionMaxSize:
            extensionMaxSize[extension] = max(extensionMaxSize[extension], fileSize)
        else:
            extensionMaxSize[extension] = fileSize

    sortedMaxSizePaths = []
    for path, maxSize in pathMaxSize.items():
        sortedMaxSizePaths.append((maxSize, path))
    sortedMaxSizePaths.sort()

    sortedMaxSizeExtensions = []
    for extension, maxSize in extensionMaxSize.items():
        sortedMaxSizeExtensions.append((maxSize, extension))
    sortedMaxSizeExtensions.sort()

    lenToRemove = len(cleanPath(repoPath, endSlash=True))
    return (
        set([path[lenToRemove:] for path in paths]),
        pathMaxSize,
        sortedMaxSizePaths,
        sortedMaxSizeExtensions,
        extensionPaths,
    )


(
    actualPaths,
    pathMaxSizeActual,
    sortedMaxSizePathsActual,
    sortedMaxSizeExtensionsActual,
    extensionPathsActual,
) = getRepoActualFileInfos(repoPath)


def getRepoHistoryFileInfos(repo, changesetNumbers=None):
    pathMaxSize = dict()
    extensionMaxSize = dict()
    extensionPaths = dict()
    removePaths = set()
    if changesetNumbers is None:
        changesetNumbers = repo
    elif not isinstance(changesetNumbers, list):
        changesetNumbers = [changesetNumbers]
    for changesetNumber in changesetNumbers:
        # print(changesetNumber)
        changeset = repo[changesetNumber]
        paths = changeset.files()
        for bytes_path in paths:
            path = bytes_path.decode("1250")
            # print(type(path))
            extension = ext(path)
            # print(path)
            # print()
            if fileName(path) in excludeFileNames:
                removePaths.add(path)
                # print(path)
            elif extension in excludeExtensions:
                removePaths.add(path)
            elif (
                extension in excludeExtensionsIfFileNotInLast
                and path not in actualPaths
            ):
                removePaths.add(path)
            elif excludeFolderNames.intersection(set(directories(path))):
                removePaths.add(path)
            else:
                if extension not in extensionPaths:
                    extensionPaths[extension] = set()
                extensionPaths[extension].add(path)
                try:
                    fileContext = changeset.filectx(bytes_path)
                    fileSize = fileContext.size()
                    if extension in extensionMaxSize:
                        extensionMaxSize[extension] = max(
                            extensionMaxSize[extension], fileSize
                        )
                    else:
                        extensionMaxSize[extension] = fileSize
                    if path in pathMaxSize:
                        pathMaxSize[path] = max(pathMaxSize[path], fileSize)
                    else:
                        pathMaxSize[path] = fileSize
                except:
                    pass
                # print(path , fileContext.size(),fileContext.isbinary())

    sortedMaxSizePaths = []
    for path, maxSize in pathMaxSize.items():
        sortedMaxSizePaths.append((maxSize, path))
    sortedMaxSizePaths.sort()

    sortedMaxSizeExtensions = []
    for extension, maxSize in extensionMaxSize.items():
        sortedMaxSizeExtensions.append((maxSize, extension))
    sortedMaxSizeExtensions.sort()

    # print(sortedMaxSizePaths)
    return (
        removePaths,
        pathMaxSize,
        sortedMaxSizePaths,
        sortedMaxSizeExtensions,
        extensionPaths,
    )


(
    removePaths,
    pathMaxSize,
    sortedMaxSizePaths,
    sortedMaxSizExtensions,
    extensionPaths,
) = getRepoHistoryFileInfos(repo)


excludeLines = ['exclude "' + removePath + '"\n' for removePath in removePaths]
writeLines("map.txt", excludeLines, encoding="cp1250")
print(sortedMaxSizExtensions)
