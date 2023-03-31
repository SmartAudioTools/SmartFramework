# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 16:10:41 2020

@author: Baptiste
"""
# from SmartFramework.string import getEncoding,_assciPartIsPrintable
from SmartFramework.files import getFileEncoding, read, readLines

# string = '鼅';encoding = 'cp1252'
# string = '€'; encoding = 'utf_16_le'
# string = '日本語版'; encoding = 'utf_16_le'
# string = '日本語版'; encoding = 'ISO-2022-JP'
# string = 'e'; encoding = 'utf_16_be'
# string = 'aé'; encoding = 'ISO-8859-1'
# string = '战无不胜的毛泽东思想万岁' ; encoding =   'HZ-GB-2312'
# string = 'é€€'; encoding = 'windows-1252'
# string = '''salut les amis\ncomment ca va? je vais vous racompter une histoire , pour avoir beaucoups de caractères et  depasser les 100.\n ça me permet d'être sur que le utf_16_be passe bien\n C'est compris ?''';encoding = 'utf_16_be'
# string = "hÃ©!\nbonjour\nvous Ãªtes prÃªts?\nmoi j'ai mangé"; encoding = 'cp1252'
# string = "Доброе утро"; encoding = 'utf_16_be'
# string = "hÃ©!\nbonjour\nvous Ãªtes prÃªts Ã\xa0 partir sur l'Ã®le de brÃ©hat ? moi j'ai mangé"; encoding = 'utf_16_be'

# string = "Съжалявам"; encoding = 'utf_16_le'
# string = "gyönyörű színésznő"; encoding = 'ISO-8859-2'
# string = "ελπίδα"; encoding = 'ISO-8859-7'
# string = "ελπίδα"; encoding = 'utf-8'
# string = "e"; encoding = 'ascii'
# string = "שלום"; encoding = 'ISO-8859-8'
# string = "鼅鼄"; encoding = 'GB18030'
# string = "salut les amis\ncomment ca va?"; encoding = 'utf_16_be'
# aé
# string = "è€€"; encoding = 'cp1252'
# string = "Âµé"; encoding = 'cp1252'
# string = "\t"; encoding = 'utf_16_le'
# string = "หน้าตาที่น่าเกลียด"; encoding = 'utf_16_le'
# string = "Â€"; encoding = 'cp1252'
string = (
    "hÃ©!\nbonjour\nvous Ãªtes prÃªts Ã\xa0 partir dans les pr\\Ã¨s ?\nnmoi j'ai mangé"
)
encoding = "cp1252"
string = "\r"
encoding = "cp1252"
# string = "salut les amis\ncomment ca va? je vais vous racompter une histoire , pour avoir beaucoups de caractères et  depasser les 100.\n ça me permet d'être sur que le utf_16_be passe bien\n C'est compris ?";encoding = "ISO-8859-1"
# string = "salut les amis\ncomment ca va? je vais vous racompter une histoire , pour avoir beaucoups de caractères et  depasser les 100.\n ça me permet d'être sur que le utf_16_be passe bien\n C'est compris ?";encoding = "utf_16_le"

bytes_ = string.encode(encoding)
with open("test.txt", "wb") as f:
    f.write(bytes_)
decoded = "".join(readLines("test.txt", keepends=True, replace_newline=False))
# encoding_detected = getEncoding(bytes_)
# decoded = read('test.txt', encoding = encoding_detected)


if string == decoded:
    print("ok")
else:
    # print(string,'('+encoding+')', '->', stringOut ,'('+encodingDetected+')','\t', )
    print(repr(string)[1:-1], "->", repr(decoded)[1:-1], "\t", encoding, "->", bytes_)
