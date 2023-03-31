# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 14:31:23 2020

@author: Baptiste
"""
import chardet
import cchardet
from SmartFramework.string import getEncoding  # ,_assciPartIsPrintable
from SmartFramework.files import read, readLines, getFileEncoding
from time import perf_counter
import itertools

cp1252_printables = "\t\n\r !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ¡¢£¤¥¦§¨©ª«¬\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"
cp1254_usual = "\t\n\r !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~€£µÀÁÂÃÄÇÈÉÊËÌÍÎÏÒÔÕÖÙÚÛÜàáâãäçèéêëìíîïòôõöùûü"
cp1254_usual_without_ÂÃ = "\t\n\r !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~€£µÀÁÄÇÈÉÊËÌÍÎÏÒÔÕÖÙÚÛÜàáâãäçèéêëìíîïòôõöùûü"
cp1254_commun = "\t\n\r !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~€£µàâçèéêëîïôùû"
cp1254_commun_double = [
    char1 + char2 for char1, char2 in itertools.product(cp1254_commun, cp1254_commun)
]
cp1252_commun_triple = [
    couple + char3
    for couple, char3 in itertools.product(cp1254_commun_double, cp1254_commun)
]
cp1252_usual_double = [
    char1 + char2 for char1, char2 in itertools.product(cp1254_usual, cp1254_usual)
]
cp1252_usual_double_without_ÂÃ = [
    char1 + char2
    for char1, char2 in itertools.product(
        cp1254_usual_without_ÂÃ, cp1254_usual_without_ÂÃ
    )
]
cp1252_usual_triple = [
    couple + char3
    for couple, char3 in itertools.product(
        cp1252_usual_double_without_ÂÃ, cp1254_usual_without_ÂÃ
    )
]

encodings_strings_from_language = {
    "ascii": (["ascii"], ["e"]),
    "simple_letter": (
        [
            "windows-1252",
            "utf_8",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        list(cp1252_printables),
    ),
    "western_european": (
        [
            "ISO-8859-1",
            "windows-1252",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        [
            "salut ! j'ai bien mangé",
            "salut les amis\ncomment ca va? je vais vous racompter une histoire , pour avoir beaucoups de caractères et  depasser les 100.\n ça me permet d'être sur que le utf_16_be passe bien\n C'est compris ?",
            "hé!\nbonjour\nvous êtes prêts?\nmoi j'ai mangé",  # pour tester readline
            (bytes(range(32, 127)) * 300).decode("ascii") + "é",
        ],
    ),
    # "double_letters_usual" :(['windows-1252','utf_8'],cp1252_usual_double),
    "double_letters_usual_interpretable_in_utf8": (
        ["windows-1252"],
        [
            "Ã€",
            "Ã£",
            "Ãµ",
            "Â€",
            "Â£",
            "Âµ",
            "Ä€",
            "Ä£",
            "Äµ",
            "Ç€",
            "Ç£",
            "Çµ",
            "È€",
            "È£",
            "Èµ",
            "É€",
            "É£",
            "Éµ",
            "Ê€",
            "Ê£",
            "Êµ",
            "Ë€",
            "Ë£",
            "Ëµ",
            "Ì€",
            "Ì£",
            "Ìµ",
            "Í€",
            "Í£",
            "Íµ",
            "Î€",
            "Î£",
            "Îµ",
            "Ï€",
            "Ï£",
            "Ïµ",
            "Ò€",
            "Ò£",
            "Òµ",
            "Ô€",
            "Ô£",
            "Ôµ",
            "Õ€",
            "Õ£",
            "Õµ",
            "Ö€",
            "Ö£",
            "Öµ",
            "Ù€",
            "Ù£",
            "Ùµ",
            "Ú€",
            "Ú£",
            "Úµ",
            "Û€",
            "Û£",
            "Ûµ",
            "Ü€",
            "Ü£",
            "Üµ",
        ],
    ),
    # "triple_letters_usual": (['windows-1252'],cp1252_usual_triple),
    # "triple_letters_commun": (['windows-1252'],cp1252_commun_triple),
    "triple_letters_commun_interpretable_in_utf8": (
        ["windows-1252"],
        [
            "à£€",
            "à££",
            "à£µ",
            "àµ€",
            "àµ£",
            "àµµ",
            "â€€",
            "â€£",
            "â€µ",
            "â£€",
            "â££",
            "â£µ",
            "âµ€",
            "âµ£",
            "âµµ",
            "ç€€",
            "ç€£",
            "ç€µ",
            "ç£€",
            "ç££",
            "ç£µ",
            "çµ€",
            "çµ£",
            "çµµ",
            "è€€",
            "è€£",
            "è€µ",
            "è£€",
            "è££",
            "è£µ",
            "èµ€",
            "èµ£",
            "èµµ",
            "é€€",
            "é€£",
            "é€µ",
            "é£€",
            "é££",
            "é£µ",
            "éµ€",
            "éµ£",
            "éµµ",
            "ê€€",
            "ê€£",
            "ê€µ",
            "ê£€",
            "ê££",
            "ê£µ",
            "êµ€",
            "êµ£",
            "êµµ",
            "ë€€",
            "ë€£",
            "ë€µ",
            "ë£€",
            "ë££",
            "ë£µ",
            "ëµ€",
            "ëµ£",
            "ëµµ",
            "î€€",
            "î€£",
            "î€µ",
            "î£€",
            "î££",
            "î£µ",
            "îµ€",
            "îµ£",
            "îµµ",
            "ï€€",
            "ï€£",
            "ï€µ",
            "ï£€",
            "ï££",
            "ï£µ",
            "ïµ€",
            "ïµ£",
            "ïµµ",
        ],
    ),
    "utf_8_cp1252_mixed": (
        ["windows-1252"],
        [
            "hé!\nbonjour\nvous êtes prêts?\nmoi j'ai mangé",  # pour tester readline
            "hÃ©!\nbonjour\nvous Ãªtes prÃªts?\nmoi j'ai mangé",  # peut arriver si mélange utf-8 et cp1252,par exemple après avoir édité un fichier utf-8 apèrs l'avoir ouvert en cp1252
            "hÃ©!\nbonjour\nvous Ãªtes prÃªts Ã\xa0 partir dans les pr\Ã¨s ?\nnmoi j'ai mangé",  # peut arriver si mélange utf-8 et cp1252
            "hÃ©!\nbonjour\nvous Ãªtes prÃªts Ã\xa0 partir sur l'Ã®le de brÃ©hat ? moi j'ai mangé",  # peut arriver si mélange utf-8 et cp1252
        ],
    ),
    "russian": (
        [
            "KOI8-R",
            "MacCyrillic",
            "IBM855",
            "IBM866",
            "ISO-8859-5",
            "windows-1251",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["Доброе утро"],
    ),
    "simplified_chinese": (
        [
            "Big5",
            "GB2312",
            "GB18030",
            "EUC-TW",
            "HZ-GB-2312",
            "ISO-2022-CN",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["战无不胜的毛泽东思想万岁"],
    ),
    "traditional_chinese": (
        ["utf_16_le", "utf_16_be", "utf_32_le", "utf_32_be"],
        ["㤂㔊"],
    ),
    "japanese": (
        [
            "EUC-JP",
            "SHIFT_JIS",
            "ISO-2022-JP",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["日本語版"],
    ),
    "korean": (
        [
            "EUC-KR",
            "ISO-2022-KR",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["매년 저는 나이를 먹습니다", "기차로 가다"],
    ),
    "Hungarian": (
        [
            "ISO-8859-2",
            "windows-1250",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["Viszontlátásra", "Viszlát", "gyönyörű színésznő"],
    ),
    "bulgarian": (
        [
            "ISO-8859-5",
            "windows-1251",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["Съжалявам", "Моля"],
    ),
    "greek": (
        [
            "ISO-8859-7",
            "windows-1253",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["φιλοξενία", "ελπίδα", "ευτυχία"],
    ),
    "hebrew": (
        [
            "ISO-8859-8",
            "windows-1255",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["אהבה", "פרצוף מכוער"],
    ),
    "thai": (
        [
            "TIS-620",
            "utf_8",
            "utf_8_sig",
            "utf_16",
            "utf_32",
            "utf_16_le",
            "utf_16_be",
            "utf_32_le",
            "utf_32_be",
        ],
        ["หน้าตาที่น่าเกลียด"],
    ),
}

"""



# tests avec encodage dans un bytes ------------------
for detectFonction in  getEncoding,chardet.detect,cchardet.detect:# :# :
    print("\n%s.%s ---------------------"%(detectFonction.__module__,detectFonction.__name__))
    tests = 0
    start = perf_counter()
    errors = 0
    succed = 0
    for encodings,strings in encodings_strings_from_language.values():
        for string in strings:
            bytes_already_tested_for_this_string = set()
            for encoding in encodings:
                try : 
                    bytes_ = string.encode(encoding )  
                except : 
                    continue
                if bytes_ in bytes_already_tested_for_this_string : 
                    continue 
                tests += 1
                bytes_already_tested_for_this_string.add(bytes_)
                error = False
                if detectFonction == getEncoding:
                    encoding_detected, decoded  = detectFonction(bytes_,return_decoded = True)	
                #print(detect)
                else :
                    encoding_detected  = detectFonction(bytes_)
                    encoding_detected = encoding_detected['encoding']  
                    if encoding_detected is not None :
                        try :
                            decoded = bytes_.decode(encoding_detected)
                        except: 
                            decoded = 'ERROR'  
                            error = True
                            errors += 1
                    else  :
                        decoded = 'No encoding detected'
                if string == decoded:
                    succed += 1
                else : 
                    if detectFonction is getEncoding or error :
                        pass
                        print(repr(string)[1:-1] ,'->', repr(decoded)[1:-1] ,'\t',encoding,'->',encoding_detected) #'->',bytes_,',assciPartIsPrintable(decoded)
    end = perf_counter()
    succed_percent = 100*succed/tests
    
    if errors  :
        error_percent = 100*errors/tests
        pass
        print('succed {:.6f}% ERROR {:.6f}% in {:.4f}msec'.format(succed_percent,error_percent,(end-start)*1000))
    else: 
        print('succed {:.6f}% in {:.4f}msec'.format(succed_percent,(end-start)*1000))
"""

# tests avec encodage dans un fichier ------------------

readers = {
    #'read': read ,
    #'readLines'  : readLines,
    "getFileEncoding": lambda path: open(
        path, "r", encoding=getFileEncoding(path)
    ).read()
}

# for readerName , reader in readers.items() : #
#    print('write -> ',readerName,'------------')
for encodings, strings in encodings_strings_from_language.values():
    for string in strings:
        bytes_already_tested_for_this_string = set()
        for encoding in encodings:
            try:
                bytes_ = string.encode(encoding)
            except:
                continue
            if bytes_ in bytes_already_tested_for_this_string:
                continue
            bytes_already_tested_for_this_string.add(bytes_)
            with open("test.txt", "wb") as f:
                f.write(bytes_)
            encoding_detected = getFileEncoding("test.txt")
            try:
                decoded = read("test.txt", encoding=encoding_detected)
            except:
                decoded = "ERROR"
            if isinstance(decoded, list):
                decoded = "\n".join(decoded)
            if string != decoded:
                pass
                print(
                    repr(string)[1:-1],
                    "->",
                    repr(decoded)[1:-1],
                    "\t",
                    encoding,
                    encoding_detected,
                )
            else:
                pass
                # print(".",end='')
