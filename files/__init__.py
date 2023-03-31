# -*- coding: utf_8 -*-
import sys
import os
import os.path
import traceback
from shutil import copy2
import codecs
import __main__
import ctypes
import cchardet
import multiprocessing
from SmartFramework.string import (
    addNewlines,
    normalizeEncoding,
    _findBestEncoding,
    encodings_not_8bit,
    encodings_with_ascii_subset,
)

if os.name == "nt":
    import win32api
    import win32file
    import win32con
    from win32com.client import Dispatch
# import queue
import locale
from collections.abc import Iterable

local_encoding = locale.getdefaultlocale()[1]
BOMS = {
    "utf_8_sig": codecs.BOM_UTF8,
    "utf_32": codecs.BOM_UTF32,
    "utf_16": codecs.BOM_UTF16,
}  # attention ne pas tester codecs.BOM_UTF16_LE avant codecs.BOM_UTF32_LE car codecs.BOM_UTF32_LE(b'\xff\xfe\x00\x00') commence par codecs.BOM_UTF16_LE  (b'\xff\xfe')


def iterable(elt):
    if not isinstance(elt, (tuple, list)):
        return [elt]
    return elt


class READ_WRITE_____________________________________________:
    pass


"""def readBytes(path):
    with open(path, 'rb') as f:
        return f.read()

def readBytesIter(path):
    with open(path,'rb') as f : 
        for line in f : 
            yield line"""


def read(path, encoding=None, replace_newline=True, return_encoding=False):
    if not isinstance(encoding, str):
        encoding = getFileEncoding(path, encodings=encoding)
    if replace_newline:
        newline = None
    else:
        newline = ""
    with open(
        path, "r", encoding=encoding, newline=newline
    ) as f:  # le newline = '' permet d'eviter de faire un scanne du fichier pour remplacer automatiquement \r\n par \n lors du read()
        decoded = f.read()
    if return_encoding:
        return decoded, encoding
    else:
        return decoded


def readLines(path, encoding=None, keepends=False, replace_newline=True, iterator=True):
    if encoding is None:
        encoding = getFileEncoding(path, encodings=encoding)
    if keepends and not replace_newline:
        newline = ""
    else:
        newline = None
    f = open(path, "r", encoding=encoding, newline=newline)
    if keepends:
        if iterator:
            return (line for line in f)
        else:
            return list(f)
    else:
        if iterator:
            return (line.rstrip("\n") for line in f)
        else:
            return [line.rstrip("\n") for line in f]


def write(path, element, encoding="utf_8_sig", newline="\n"):
    # le utf_8_sig par defaut permet de rajotuer le BOM au début du fichier permet d'accelerer sa lecture et de limiter la mémoire necessaire en évitant d'avoir à le mettre une première fois en mémoire et de devoir deviner l'encodage avec cchardet.
    # le newline = "\n" par defaut permet d'acceler ecriture en evitant à python de scanner le fichier pour ramplacer tout les \n par \r\n
    if isinstance(element, bytes):
        with open(path, "wb") as f:
            f.write(element)
    elif isinstance(element, str):
        with open(path, "w", encoding=encoding, newline=newline) as f:
            f.write(element)
    elif isinstance(element, Iterable):  # attention les bytes et str son Iterable !
        try:
            with open(path, "wb") as f:
                f.writelines(addNewlines(element, newline=newline))
        except:
            with open(
                path, "w", encoding=encoding, newline=""
            ) as f:  # ajoute le BOM s'il faut
                f.writelines(addNewlines(element, newline=newline))
    else:
        raise Exception()
    return path


__path_encoding__ = {}


def addInFile(path, element, encoding=None, newline="\n", default_encoding="utf_8_sig"):
    if isinstance(element, bytes):
        with open(path, "ab") as f:
            if f.tell() != 0 and newline:
                f.write(newline.encode("ascii"))
            f.write(element)
    elif isinstance(element, str):
        if not isinstance(encoding, str):
            if not os.path.exists(path):
                encoding = default_encoding
            else:
                encoding = __path_encoding__.get(
                    path, getFileEncoding(path, encodings=encoding)
                )  # très couteux si appells succéssif !
        __path_encoding__[path] = encoding
        with open(path, "a", encoding=encoding, newline=newline) as f:
            if f.tell() != 0 and newline:
                f.write(newline)
            f.write(element)
    elif isinstance(element, Iterable):
        first = True
        prior_line = None
        for line in element:
            if first:
                first = False
                if isinstance(line, bytes):
                    if isinstance(newline, str):
                        newline = newline.encode("ascii")
                    f = open(path, "ab")
                    if f.tell() != 0 and newline:
                        f.write(newline)
                else:
                    if not isinstance(encoding, str):
                        if not os.path.exists(path):
                            encoding = default_encoding
                        else:
                            encoding = __path_encoding__.get(
                                path, getFileEncoding(path, encodings=encoding)
                            )  # très couteux si appells succéssif !
                    __path_encoding__[path] = encoding
                    f = open(path, "a", encoding=encoding, newline=newline)
                    if f.tell() != 0 and newline:
                        f.write(newline)
            else:
                f.write(prior_line)
                f.write(newline)
            prior_line = line
        f.write(prior_line)
        f.close()
    else:
        raise Exception()


def replaceInFile(path, elt, toElt, encoding=None, silent=False):
    if not silent:
        print(path)
    string, encoding = read(path, encoding=encoding, return_encoding=True)
    if string.find(elt) != -1:
        newstring = string.replace(elt, toElt)
        write(path, newstring, encoding=encoding)


class FILE_INFOS________________________________________________:
    pass


# @profile
def getFileEncoding(path, encodings=None, return_newline=False):
    if encodings is None:
        encodings = [
            "ascii",
            "utf_8",
            "cp1252",
            "cp1252_mixed_utf_8",
            "utf_16",
            "utf_32",
            "others",
        ]
    else:
        encodings = [normalizeEncoding(enc) for enc in encodings]
    encoding_set = set(encodings)
    only_utf_8_cp1252_local = not bool(
        encoding_set
        - set(
            [
                "ascii",
                "utf_8",
                "utf_8_sig",
                "cp1252",
                "cp1252_mixed_utf8",
                local_encoding,
            ]
        )
    )
    chardet_confidence_threshold = 0.80
    enable_cp1252_mixed_utf_8 = "cp1252_mixed_utf_8" in encodings
    detect_utf16_utf32 = ("utf_16" in encodings) or ("utf_32" in encodings)
    for enc in encodings:
        if enc in encodings_with_ascii_subset:
            encoding_if_ascii = enc
            break
    else:
        encoding_if_ascii = "ascii"

    with open(path, "rb") as f:
        # Look for BOM
        raw = f.read(4)  # will read less if the file is smaller
        for encoding, bom in BOMS.items():
            if raw.startswith(bom):
                encoding = encoding.lower()
                if return_newline:
                    f.seek(0)
                    line = (
                        f.readline()
                    )  # ne sépare pas les "\r" !  va lire tout le ficher si '\r' !
                    len_line = len(line)
                    newline = "\n"
                    if len_line:
                        if line[-1] == 10:
                            if len_line > 1 and line[-2] == 13:
                                newline = "\r\n"
                        elif 13 in line:  # versions Mac avant OS X
                            newline = "\r"
                    return encoding, newline

                else:
                    return encoding
        else:
            encoding = None
            detector = cchardet.UniversalDetector()
        f.seek(0)
        # if return_queue:
        #    rawLinesQueue = queue.SimpleQueue()
        only_ascii = True
        only_utf_8 = True
        only_cp1252_usuals = True
        only_cp1252_utf_8_keyboard_accessible = True
        only_cp1252_usuals_mixed_utf_8 = enable_cp1252_mixed_utf_8
        newline = None
        bytes_with_A_tilde = False
        chardet_encoding = None
        i = -1
        for (
            bytes_
        ) in (
            f
        ):  # contrairement à readlines(), a priori ne copie pas tout en mémoire , sauf si fichier avec retour à la ligne '\r' fichiers  versions Mac avant OS X
            i += 1
            # print(i)
            len_line = len(bytes_)
            if newline is None:  # ATTENTIN NE GERERA PAS DES FINS DE LIGNES MELANGEES
                newline = "\n"
                if len_line:
                    if bytes_[-1] == 10:
                        if len_line > 1 and bytes_[-2] == 13:
                            newline = "\r\n"
                    elif 13 in bytes_:
                        newline = "\r"  # versions Mac avant OS X

            # detect utf_16_le,utf_16_be, utf_32_le,utf_32_be
            if i < 2 and len_line and detect_utf16_utf32:
                if i == 0:
                    if (
                        bytes_[-1] == 10
                        and not len_line % 2
                        and len_line > 1
                        and bytes_[-2] == 0
                    ):
                        if len_line > 3 and bytes_[-3] == 0 and bytes_[-4] == 0:
                            encoding = "utf_32_be"
                        else:
                            encoding = "utf_16_be"
                        break
                elif bytes_[0] == 0:  # i == 1
                    if len_line > 2 and bytes_[1] == 0 and bytes_[2] == 0:
                        encoding = "utf_32_le"
                    else:
                        encoding = "utf_16_le"
                    break
            if only_cp1252_usuals_mixed_utf_8:
                try:
                    bytes_.decode("cp1252_usuals_mixed_utf_8")
                except:
                    only_cp1252_usuals_mixed_utf_8 = False
                    only_cp1252_usuals = False
            if only_cp1252_usuals:
                try:
                    bytes_.decode("cp1252_usuals")
                except:
                    only_cp1252_usuals = False
            if not bytes_.isascii():
                only_ascii = False
                if not bytes_with_A_tilde and 195 in bytes_:
                    bytes_with_A_tilde = True
                if only_utf_8:
                    try:
                        bytes_.decode("utf_8")
                    except:
                        only_utf_8 = False
                        only_cp1252_utf_8_keyboard_accessible = False
                        if chardet_encoding == "utf_8":
                            break
                    else:
                        if only_cp1252_utf_8_keyboard_accessible:
                            if 195 in bytes_:
                                only_cp1252_utf_8_keyboard_accessible = False
                            else:
                                try:
                                    bytes_.decode("cp1252_utf_8_keyboard_accessible")
                                except:
                                    only_cp1252_utf_8_keyboard_accessible = False
            if chardet_encoding is None:
                detector.feed(bytes_)
                if (
                    detector.done
                ):  # permet de ne pas attendre fin du fichier pour être sur que utf_8
                    detector.close()
                    chardet_encoding = normalizeEncoding(detector.result["encoding"])
                    if chardet_encoding == "latin_1":
                        chardet_encoding = "cp1252"
                    if enable_cp1252_mixed_utf_8:
                        continue
                    encoding = chardet_encoding
                    break

        # Test others encoding ----------------------------------------------------
        if encoding is None:
            if only_utf_8_cp1252_local:
                if only_ascii:
                    encoding = "ascii"
                elif only_cp1252_utf_8_keyboard_accessible:
                    encoding = "cp1252"
                elif only_utf_8:
                    encoding = "utf_8"
                elif local_encoding == "cp1252":
                    encoding = "cp1252"  # asssume "cp1252"
                else:
                    detector.close()
                    result = detector.result
                    chardet_encoding = normalizeEncoding(result["encoding"])
                    if chardet_encoding == "latin_1":
                        chardet_encoding = "cp1252"
                    if chardet_encoding == local_encoding:
                        encoding = local_encoding
                    else:
                        encoding = "cp1252"
            else:
                if not only_ascii and only_utf_8:
                    if only_cp1252_utf_8_keyboard_accessible:
                        encoding = "cp1252"
                    else:
                        encoding = "utf_8"
                else:
                    detector.close()
                    result = detector.result
                    chardet_confidence = result["confidence"]
                    chardet_encoding = normalizeEncoding(result["encoding"])
                    if chardet_encoding == "latin_1":
                        chardet_encoding = "cp1252"
                    if (
                        chardet_confidence is not None
                        and chardet_confidence > chardet_confidence_threshold
                    ):
                        if chardet_encoding not in (
                            "utf_8",
                            "ascii",
                        ):  # non ce n'est pas de l'utf_8 sinon on l'aurait only_utf_8 == True et on aurait retourné l'encoding au dessus , exemple avec 'ÃƒÂ©Ã©é'.encode("cp1252")
                            if (
                                enable_cp1252_mixed_utf_8
                                and only_cp1252_usuals_mixed_utf_8
                                and bytes_with_A_tilde
                            ):
                                encoding = "cp1252_mixed_utf_8"
                            else:
                                encoding = chardet_encoding

                    # chardet n'est pas sûre de lui -> tente avec cp1252 restreint au caractères usuels -----

                    if encoding is None:
                        if only_cp1252_usuals:
                            if only_ascii:
                                encoding = encoding_if_ascii
                            else:
                                encoding = "cp1252"
                        elif (
                            enable_cp1252_mixed_utf_8
                            and only_cp1252_usuals_mixed_utf_8
                            and bytes_with_A_tilde
                        ):
                            encoding = "cp1252_mixed_utf_8"
                        else:
                            to_try_after = []
                            if (
                                chardet_confidence is not None
                                and chardet_encoding
                                not in (
                                    "utf_8",
                                    "ascii",
                                )
                            ):  # sinon on serait pas là
                                if chardet_confidence > 0.55:
                                    encoding = chardet_encoding
                                else:
                                    to_try_after = [chardet_encoding]

                            if encoding is None and len_line > 1:
                                encoding = _findBestEncoding(
                                    bytes_,
                                    to_try_after
                                    + encodings_not_8bit
                                    + [
                                        "utf_16_be",
                                        "utf_16_le",
                                        "utf_32_be",
                                        "utf_32_le",
                                    ],
                                )

                            # no codec was found, take ascii or local_encoding -----------------
                            # pas sûr qu'on puisse arriver ici si _findBestEncoding retourne de toute facon quelque chose
                            if encoding is None:
                                if only_ascii:
                                    encoding = "ascii"
                                else:
                                    encoding = local_encoding
        if encoding == "ascii":
            encoding = encoding_if_ascii
        if return_newline:
            return encoding, newline
        else:
            return encoding


def driveExist(letter):
    # return (win32file.GetLogicalDrives() >> (ord(letter.upper()) - 65) & 1) != 0
    path = letter[0] + ":"
    oldmode = ctypes.c_uint()
    kernel32 = ctypes.WinDLL("kernel32")
    SEM_FAILCRITICALERRORS = 1
    SEM_NOOPENFILEERRORBOX = 0x8000
    SEM_FAIL = SEM_NOOPENFILEERRORBOX | SEM_FAILCRITICALERRORS
    kernel32.SetThreadErrorMode(SEM_FAIL, ctypes.byref(oldmode))
    value = os.path.exists(path)
    kernel32.SetThreadErrorMode(oldmode, ctypes.byref(oldmode))
    return value


def comment(path):
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation"
        )[0]
        strInfoPath = "\\StringFileInfo\\%04X%04X\\%s" % (lang, codepage, "Comments")
        return win32api.GetFileVersionInfo(path, strInfoPath)
    except:
        return None


def description(path):
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


class MANIPULATIONS_______________________________________________:
    pass


def replaceInNames(fromStr, toStr, paths, silent=False):
    folders = []
    files = []
    for path in paths:
        if os.path.isdir(path):
            if path.find(fromStr) != -1:
                folders.append(path)
        else:
            files.append(path)
    # replace in file names
    for path in files:
        folder, name, ext = splitPath(path)
        if name.find(fromStr) != -1:
            newName = name.replace(fromStr, toStr)
            newPath = joinPath(folder, newName, ext)
            if not silent:
                print(path, " -> ", newPath)
            os.rename(path, newPath)

    # replace in directory names
    splitedDirectories = []
    for path in folders:
        directories = path.split("/")
        splitedDirectories.append(directories)
    while splitedDirectories:
        nextIterationSplitedDirectories = []
        for directories in reversed(sorted(splitedDirectories)):
            lastDirectory = directories[-1]
            if lastDirectory.find(fromStr) != -1:
                newLastDirectory = lastDirectory.replace(fromStr, toStr)
                newPath = "/".join(directories[:-1] + [newLastDirectory])
                path = "/".join(directories)
                if not silent:
                    print(path, " -> ", newPath)
                os.rename(path, newPath)
            if len(directories) > 1:
                nextIterationSplitedDirectories.append(directories[:-1])
        splitedDirectories = nextIterationSplitedDirectories


def createFolder(path):
    folder = directory(path)
    if not os.path.isdir(folder):
        os.makedirs(folder)


def removeExistingPathAndCreateFolder(path):
    if os.path.exists(path):
        os.remove(path)
    folder = directory(path)
    if not os.path.isdir(folder):
        os.makedirs(folder)


def dragAndDrop(
    callback,
    extension=None,
    exploreFolders=True,
    recursive=False,
    endPause=False,
    group=False,
    processes=1,
):
    try:
        if isinstance(extension, str):
            extension = [extension]

        # os.chdir(directory(__file__))
        cleanDropNames(sys.argv)
        # sys.argv = [None,'D:/Dropbox/Smart Audio Tools/DAT']
        if len(sys.argv) == 1:
            print("glissez un fichier ou repertoir sur script")
            os.system("pause")
            sys.exit()

        paths = []
        for path in sys.argv[1:]:
            if os.path.isdir(path):
                if exploreFolders:
                    paths.extend(searchExt(path, extension, recursive=recursive))
            elif (extension is None) or (ext(path) in extension):
                paths.append(path)
        if group:
            callback(paths)
        else:
            if processes > 1 and len(paths) > 1:
                pool = multiprocessing.Pool(processes=processes)
                pool.map(callback, paths)
            else:
                for path in paths:
                    callback(path)
        if endPause:
            os.system("pause")

    except:
        # print("erreure avec le fichier : %s" % jsonPath)
        traceback.print_exc()
        os.system("pause")


def makeLink(
    path="",
    target="",
    comment=None,
    icon=None,
):
    # folder= directory(path)
    # if not os.path.exists(folder):
    #    os.makedirs(folder)
    if ext(path) == "url":
        write(path, "[InternetShortcut]\nURL=%s" % target)
    else:
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target.replace("/", "\\")
        # shortcut.WorkingDirectory = os.path.dirname(target)
        if icon is not None:
            shortcut.IconLocation = icon
        if comment is not None:
            shortcut.Description = comment
        shortcut.save()


def removeIcon(folder):
    change = setFileAttributes(folder, win32con.FILE_ATTRIBUTE_SYSTEM, False)

    destopPath = folder + "/desktop.ini"
    if os.path.exists(destopPath):
        os.remove(destopPath)
    iconPaths = chercheExt(folder, "ico")
    for iconPath in iconPaths:
        os.remove(iconPath)
    imagePath = folder + "/Folder.jpg"
    if (
        os.path.exists(imagePath) and change
    ):  # il faut renomer et remtre Folder.jpg pour debloquer l'affichage du dossier
        os.rename(imagePath, imagePath + ".temp")
        os.rename(imagePath + ".temp", imagePath)


def setIcon(folder, iconSrc=None, copy=True):
    if os.path.isdir(folder):
        if iconSrc:
            setFileAttributes(folder, win32con.FILE_ATTRIBUTE_SYSTEM)

            if copy:
                iconPath = changeDirectory(iconSrc, folder)
                if not os.path.exists(iconPath):
                    copy2(iconSrc, iconPath)
                setFileAttributes(iconPath, win32con.FILE_ATTRIBUTE_HIDDEN)

            desktopPath = joinPath(folder, "desktop", "ini")
            if os.path.exists(desktopPath):
                setFileAttributes(desktopPath, win32con.FILE_ATTRIBUTE_HIDDEN, False)
            if copy:
                iconSrc = fileName(iconSrc)
            write(
                desktopPath,
                "[.ShellClassInfo]\nIconFile=.\\%s\r\nIconIndex=0" % iconSrc,
                encoding="utf_8_sig",
            )
            setFileAttributes(desktopPath, win32con.FILE_ATTRIBUTE_HIDDEN)
        else:
            removeIcon(folder)
    else:
        print(folder + " introuvable")


def delEmptyDirectories(path):
    if not os.path.isdir(path):
        return
    empty = True
    for fileName in os.listdir(path):
        subPath = os.path.join(path, fileName)
        if os.path.isdir(subPath):
            if not delEmptyDirectories(subPath):
                empty = False
        else:
            empty = False
    if empty:
        os.rmdir(path)
    return empty


def setFileAttributes(filename, fileattribute, value=True):
    """Turn a specific file attribute on or off, leaving the other
    attributes intact.
    """
    filename = win32api.GetShortPathName(filename)
    # print(filename)
    bitvector = win32file.GetFileAttributes(filename)
    # print(bin(bitvector))
    # print(bin(fileattribute))
    if value:
        newbitvector = bitvector | fileattribute
    else:
        newbitvector = bitvector & (~fileattribute)
        # print(bin(bitvector))
    if newbitvector != bitvector:
        # print("change attribut pour : ",filename)
        win32file.SetFileAttributes(filename, newbitvector)
        return True
    return False


def syncFolder(src, dst, extensions=None, recursive=False, replace_dict=None):
    src = cleanPath(src)
    dst = cleanPath(dst)
    len_src = len(src)
    src_paths = search(src, extensions=extensions, recursive=recursive)
    src_dst_dict = dict()
    for src_path in src_paths:
        src_path_end = src_path[len_src:]
        if replace_dict is not None:
            for key, value in replace_dict.items():
                src_path_end = src_path_end.replace(key, value)
        src_dst_dict[src_path] = dst + src_path_end
    existing_dst_paths = set(search(dst, extensions=extensions, recursive=recursive))
    for src_path, dst_path in src_dst_dict.items():
        if dst_path not in existing_dst_paths:
            copy2(src_path, dst_path)
        else:
            existing_dst_paths.remove(dst_path)
            if os.path.getmtime(src_path) > os.path.getmtime(dst_path):
                copy2(src_path, dst_path)
    for existing_dst_path in existing_dst_paths:
        os.remove(existing_dst_path)


class SEARCHS____________________________________:
    pass


def search(
    paths,
    extensions=None,
    excludeFolders=[],
    recursive=False,
    name=None,
    returnFiles=True,
    returnFolders=False,
    returnFirst=False,
):
    # permet de lire fichier avec nom unicode

    # mise en forme des paths :
    if isinstance(paths, str):
        paths = [paths]
    elif isinstance(paths, list) or isinstance(paths, tuple):
        paths = [e for e in paths]
    else:
        raise Exception("findFile ne prend que des strings , list ou tuple de string")
    # mise en forme des extensions :
    if extensions is None:
        extensionsLower = None
    else:
        if isinstance(extensions, str):
            extensionsLower = [extensions.lower()]
        elif isinstance(extensions, list) or isinstance(extensions, tuple):
            extensionsLower = [e.lower() for e in extensions]
        else:
            raise Exception(
                "cherche ne prend pour extensions que des strings , list ou tuple de string ou None"
            )
        set(extensionsLower)

    result = []
    for path in paths:
        path = cleanPath(path)
        if os.path.exists(path):
            if os.path.isdir(path):
                rootdirectory = path
            else:
                rootdirectory = directory(path)

            for root, dirs, fileNames in os.walk(rootdirectory):
                # dirs et fileNames sont des iterateurs, je ne les utilise pas mais je pourais les utiliser plutot que de tester os.path.exists(testPath)?

                for excludeFolder in excludeFolders:
                    if excludeFolder in dirs:
                        dirs.remove(excludeFolder)
                if name is not None:
                    testPath = joinPath(root, name)
                    if os.path.exists(testPath):
                        if os.path.isdir(testPath):
                            if returnFolders:
                                if returnFirst:
                                    return testPath
                                else:
                                    result.append(testPath)
                        elif returnFiles:
                            if returnFirst:
                                return testPath
                            else:
                                result.append(testPath)
                else:
                    if returnFiles:
                        for fileName in fileNames:
                            if (extensionsLower is None) or (
                                ext(fileName) in extensionsLower
                            ):
                                result.append(joinPath(root, fileName))
                    if returnFolders:
                        for d in dirs:
                            result.append(joinPath(root, d))
                if not recursive:
                    del dirs[:]
    if returnFirst:
        return None
    else:
        return sorted(result)


chercher = search


def searchDirectories(rootdirectory, recursive=False, name=None):
    """cherche un dossier ou tous les dossiers, dans un dossier, eventuellemnet recursivement"""
    rootdirectory = cleanPath(rootdirectory)
    result = []
    if recursive == False:
        fileNames = os.listdir(rootdirectory)
        for fileName in fileNames:
            path = joinPath(rootdirectory, fileName)
            if os.path.isdir(path) and (name is None or name == fileName):
                result.append(path)
    else:
        for root, dirs, fileNames in os.walk(rootdirectory):
            for dir in dirs:
                if name is None or name == dir:
                    result.append(cleanPath(root) + "/" + dir)
    result.sort()
    return result


chercheDirectories = searchDirectories


def searchExt(rootdirectory, extensions, recursive=False, ignoreFolderName=None):
    if ignoreFolderName:
        if isinstance(ignoreFolderName, str):
            ignoreFolderName = [ignoreFolderName]
    # permet de lire fichier avec nom unicode
    rootdirectories = [
        cleanPath(root, endSlash=True) for root in iterable(rootdirectory)
    ]
    # mise en forme des extensions :
    extensionsLower = set([e.lower() for e in iterable(extensions)])
    # recherche des fichiers
    result = []
    for rootdirectory in rootdirectories:
        if recursive == False:
            fileNames = os.listdir(rootdirectory)
            for fileName in fileNames:
                if ext(fileName) in extensionsLower:
                    result.append(joinPath(rootdirectory, fileName))
        else:
            for root, dirs, fileNames in os.walk(rootdirectory):
                # print(root)
                if ignoreFolderName:
                    for x in ignoreFolderName:
                        if x in dirs:
                            dirs.remove(x)
                for fileName in fileNames:
                    if ext(fileName) in extensionsLower:
                        result.append(joinPath(root, fileName))
        result.sort()
    return result


chercheExt = searchExt


def findFile(paths, fileName, recursive=False):
    return findFileOrFolder(paths, fileName, recursive=recursive, returnFolder=False)


def findFolder(paths, fileName, recursive=False):
    return findFileOrFolder(paths, fileName, recursive=recursive, returnFile=False)


def findFileOrFolder(
    paths, fileName, recursive=False, returnFile=True, returnFolder=True
):
    # mise en forme des paths :
    if isinstance(paths, str):
        paths = [paths]
    elif isinstance(paths, list) or isinstance(paths, tuple):
        paths = [e for e in paths]
    else:
        raise Exception("findFile ne prend que des strings , list ou tuple de string")
    name, ext = splitfileName(fileName)
    for path in paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                rootdirectory = path
            else:
                rootdirectory = directory(path)
            if recursive == False:
                testPath = joinPath(rootdirectory, name, ext)
                if os.path.exists(testPath):
                    if returnFolder and returnFile:
                        return testPath
                    elif os.path.isdir(testPath):
                        if returnFolder:
                            return testPath
                    elif returnFile:
                        return testPath
            else:
                for root, dirs, fileNames in os.walk(rootdirectory):
                    # dirs et fileNames sont des iterateurs, je ne les utilise pas mais je pourais les utiliser plutot que de tester os.path.exists(testPath)?
                    testPath = joinPath(root, name, ext)
                    # print(root)
                    # print(name)
                    if os.path.exists(testPath):
                        if returnFolder and returnFile:
                            return testPath
                        elif os.path.isdir(testPath):
                            if returnFolder:
                                return testPath
                        elif returnFile:
                            return testPath
    return None


class PATH_TOOLS______________________________________________:
    pass


def cleanPath(path, endSlash=False):
    cleanedPath = path.replace("\\", "/").replace("//", "\\\\")
    if len(cleanedPath) > 0:
        if cleanedPath[0].islower() and len(cleanedPath) > 1 and cleanedPath[1] == ":":
            cleanedPath = cleanedPath[0].upper() + cleanedPath[1:]
        if cleanedPath[-1] == "/":
            if not endSlash:
                cleanedPath = cleanedPath[:-1]
        else:
            if endSlash:
                cleanedPath = cleanedPath + "/"
    return cleanedPath


def letter(path):
    return os.path.splitdrive(path)[0]


def directory(path):
    # realpath   = os.path.realpath(path)
    # return cleanPath(os.path.dirname(realpath))
    return cleanPath(os.path.dirname(path))


def directories(path):
    return directory(path).split("/")


def name(path):
    return splitPath(path)[1]


def ext(path):
    return os.path.splitext(path)[1][1:].lower()


def fileName(path):
    directory, fileName = os.path.split(path)
    return fileName


def splitfileName(fileName):
    name, ext = os.path.splitext(fileName)
    ext = ext[1:].lower()
    return name, ext


def splitPath(path):
    # splitFileName ne separe pas le nom du drive , car n'aura quasiment jamais a changer le nom du drive
    if path:
        # realpath   = os.path.realpath(path)
        # directory , fileName= os.path.split(realpath )
        directory, fileName = os.path.split(path)
        directory = directory.replace("\\", "/").replace(
            "//", "\\\\"
        )  # pour etre ok avec serveurs
        name, ext = os.path.splitext(fileName)
        ext = ext[1:].lower()
        return directory, name, ext
    else:
        return "", "", ""


def joinPath(directory, name, ext=None):
    if directory:
        if name:
            string = cleanPath(directory, endSlash=True) + name
        else:
            string = cleanPath(directory)
    else:
        string = name
    if name and ext:
        string = string + "." + ext
    return string


def changeExt(path, ext):
    return os.path.splitext(path)[0] + "." + ext


def changeLetter(path, newLetter=None):
    if newLetter:
        return newLetter + ":" + os.path.splitdrive(path)[1]
    else:
        return path


def changeDirectory(path, newDirectory):
    return joinPath(newDirectory, fileName(path))


def addToName(path, toAdd):
    directory, name, ext = splitPath(path)
    return joinPath(directory, name + toAdd, ext)


def addToFolder(path, toAdd):
    directory, name, ext = splitPath(path)
    return joinPath(directory + toAdd, name, ext)


def getPackagePath(path):
    root = directory(path)
    while os.path.exists(joinPath(root, "__init__.py")):
        package_path = root
        root = os.path.dirname(root)
    return package_path


def getPackagePathAndModulNameFromPath(path):
    path = cleanPath(path)
    root = os.path.dirname(path)
    package_path = root
    while os.path.exists(joinPath(root, "__init__.py")):
        package_path = root
        root = os.path.dirname(root)
    module = os.path.splitext(path[len(root) + 1 :])[0].replace("/", ".")
    return package_path, module


def packagepath_package_subpackage_module_from_Path(path):
    path = cleanPath(path)
    root = os.path.dirname(path)
    package_path = root
    while os.path.exists(joinPath(root, "__init__.py")):
        package_path = root
        root = os.path.dirname(root)
    module = os.path.splitext(path[len(root) + 1 :])[0].replace("/", ".")
    package = module.split(".", 1)[0]
    sub_package = module.rsplit(".", 1)[0]
    return package_path, package, sub_package, module


class WINDOWS_TOOLS____________________________________:
    pass


def replaceNonDosFile(s):
    # if type(s) != unicode :
    #    print('non unicode:', s)
    for c in '\/:*?"<>|':
        s = s.replace(c, "_")
    return s


def replaceNonDosDirectory(s):
    for c in '\/:*?"<>|':
        s = s.replace(c, "_")
    while s[-1] == ".":
        s = s[:-1]
    return s


def longPath(path):
    if path.find("~") != -1:
        import win32api

        path = win32api.GetLongPathName(path)
    return path.replace("\\", "/").replace("//", "\\\\")


def cleanDropNames(args):
    """remet en formes les noms de fichier en arguments lors d'un drop sur fichier .py , pour
    remettre sous forme d'un seul nom de fichier , les noms de fichiers avec espaces que windows a splite....
    (merci microsoft)
    Rem : on a probleme apres avoir active le drag-n-drop avec la clef de registre ci-dessous mis dans un fichier .reg
        Windows Registry Editor Version 5.00

        [HKEY_CLASSES_ROOT\Python.File\shellex\DropHandler]
        @="{86C86720-42A0-1069-A2E8-08002B30309D}"

        [HKEY_CLASSES_ROOT\Python.NoConFile\shellex\DropHandler]
        @="{86C86720-42A0-1069-A2E8-08002B30309D}"

        [HKEY_CLASSES_ROOT\Python.CompiledFile\shellex\DropHandler]
        @="{86C86720-42A0-1069-A2E8-08002B30309D}"

    un activatio avec la clef ci-dessous devrait resoudre le probleme mais ne marche pas sur mon windows 7
        REGEDIT4

        [HKEY_CLASSES_ROOT\Python.File\shellex\DropHandler]
        @="{60254CA5-953B-11CF-8C96-00AA00B8708C}"

        [HKEY_CLASSES_ROOT\Python.NoConFile\shellex\DropHandler]
        @="{60254CA5-953B-11CF-8C96-00AA00B8708C}"

        [HKEY_CLASSES_ROOT\Python.CompiledFile\shellex\DropHandler]
        @="{60254CA5-953B-11CF-8C96-00AA00B8708C}"

    """

    if os.name == "nt":
        newArgs = []
        for arg in args:
            if arg.find(":") == 1 or len(newArgs) == 0:
                newArgs.append(arg)
            else:
                newArgs[-1] = newArgs[-1] + " " + arg

        # remet tout dans arg pour pas a avoir a retourner de valeure
        for i in range(len(args)):
            del args[0]

        for newArg in newArgs:
            newArg = longPath(newArg)
            args.append(newArg)


if hasattr(__main__, "__file__"):
    # peut planter (notament dans console ou designer )
    # mainPath = __main__.__file__ ne marche pas avec spyder 5 , transforme en lowercase
    # if os.name == "nt":
    #    mainPath = win32api.GetLongPathNameW(
    #        win32api.GetShortPathName(__main__.__file__)
    #    )  #
    mainPath = __main__.__file__
    mainName = name(mainPath)
else:
    mainPath = None
    mainName = None
