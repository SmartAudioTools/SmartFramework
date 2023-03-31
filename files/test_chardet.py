# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 14:31:23 2020

@author: Baptiste
"""
import chardet
import cchardet
from SmartFramework.string import (
    getEncoding,
    normalizeEncoding,
)  # ,_assciPartIsPrintable
from SmartFramework.files import read, readLines, getFileEncoding
from time import perf_counter
import itertools

ascii_printable = "\t\n\r !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
cp1252_printables = "€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ¡¢£¤¥¦§¨©ª«¬\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"
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
    "ascii_letter": (["ascii"], list(ascii_printable)),
    "cp1252_letter": (
        [
            "cp1252",
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
            "cp1252",
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
            # "salut ! j'ai bien mangé",
            "salut les amis\ncomment ca va? je vais vous racompter une histoire , pour avoir beaucoups de caractères et  depasser les 100.\n ça me permet d'être sur que le utf_16_be passe bien\n C'est compris ?",
            "hé!\nbonjour\nvous êtes prêts?\nmoi j'ai mangé",  # pour tester readline
            (bytes(range(32, 127)) * 300).decode("ascii") + "é",
        ],
    ),
    "double_letters_usual": (["cp1252", "utf_8"], cp1252_usual_double),
    #'double_letters_usual_interpretable_in_utf8' : (['cp1252'],['Ã€','Ã£','Ãµ','Â€','Â£','Âµ','Ä€','Ä£','Äµ','Ç€','Ç£','Çµ','È€','È£','Èµ','É€','É£','Éµ','Ê€','Ê£','Êµ','Ë€','Ë£','Ëµ','Ì€','Ì£','Ìµ','Í€','Í£','Íµ','Î€','Î£','Îµ','Ï€','Ï£','Ïµ','Ò€','Ò£','Òµ','Ô€','Ô£','Ôµ','Õ€','Õ£','Õµ','Ö€','Ö£','Öµ','Ù€','Ù£','Ùµ','Ú€','Ú£','Úµ','Û€','Û£','Ûµ','Ü€','Ü£','Üµ']),
    # "triple_letters_usual": (['cp1252'],cp1252_usual_triple),
    # "triple_letters_commun": (['cp1252'],cp1252_commun_triple),
    #'triple_letters_commun_interpretable_in_utf8' : (['cp1252'],['à£€','à££','à£µ','àµ€','àµ£','àµµ','â€€','â€£','â€µ','â£€','â££','â£µ','âµ€','âµ£','âµµ','ç€€','ç€£','ç€µ','ç£€','ç££','ç£µ','çµ€','çµ£','çµµ','è€€','è€£','è€µ','è£€','è££','è£µ','èµ€','èµ£','èµµ','é€€','é€£','é€µ','é£€','é££','é£µ','éµ€','éµ£','éµµ','ê€€','ê€£','ê€µ','ê£€','ê££','ê£µ','êµ€','êµ£','êµµ','ë€€','ë€£','ë€µ','ë£€','ë££','ë£µ','ëµ€','ëµ£','ëµµ','î€€','î€£','î€µ','î£€','î££','î£µ','îµ€','îµ£','îµµ','ï€€','ï€£','ï€µ','ï£€','ï££','ï£µ','ïµ€','ïµ£','ïµµ']),
    "utf_8_cp1252_mixed": (
        ["cp1252_mixed_utf_8"],
        [
            "hÃ©!\nbonjour\nvous Ãªtes prÃªts?\nmoi j'ai mangé",  # peut arriver si mélange utf-8 et cp1252,par exemple après avoir édité un fichier utf-8 apèrs l'avoir ouvert en cp1252
            "hÃ©!\nbonjour\nvous Ãªtes prÃªts Ã\xa0 partir dans les pr\Ã¨s ?\nnmoi j'ai mangé",  # peut arriver si mélange utf-8 et cp1252
            "hÃ©!\nbonjour\nvous Ãªtes prÃªts Ã\xa0 partir sur l'Ã®le de brÃ©hat ? moi j'ai mangé",  # peut arriver si mélange utf-8 et cp1252
            "hé!\nbonjour\nvous êtes prêts à partir sur l'île de bréhat ?moi j'ai mangÃ©",  # peut arriver si mélange utf-8 et cp1252
            """La Marseillaise est un chant patriotique de la Révolution française adopté par la France comme hymne national : une première fois par la Convention pendant neuf ans du 14 juillet 1795 jusqu'à l'Empire en 1804, puis en 1879 sous la Troisième République1.\nLes six premiers couplets sont écrits par Rouget de Lisle2 sous le titre de Chant de guerre pour l'armée du Rhin3 en 1792 pour l'armée du Rhin à Strasbourg, à la suite de la déclaration de guerre de la France à l'Autriche. Dans ce contexte originel, La Marseillaise est un chant de guerre révolutionnaire, un hymne à la liberté, un appel patriotique à la mobilisation générale et une exhortation au combat contre la tyrannie et l'invasion étrangère.\nLa Marseillaise est décrétée chant national le 14 juillet 1795 (26 messidor an III) par la Convention, à l'initiative du Comité de salut public. Abandonnée en 1804 sous l’Empire et remplacée par le Chant du départ, elle est reprise en 1830 pendant la révolution des Trois Glorieuses qui porte Louis-Philippe Ier au pouvoir. Berlioz en élabore une orchestration qu’il dédie à Rouget de Lisle. Mais Louis-Philippe impose La Parisienne, chant plus modéré. La Marseillaise est de nouveau interdite sous le second Empire3.\nLa IIIe République en fait l'hymne national le 14 février 1879 et, en 1887, une « version officielle » est adoptée en prévision de la célébration du centenaire de la Révolution.\nLe 14 juillet 1915, les cendres de Rouget de Lisle sont transférées aux Invalides.\nPendant la période du régime de Vichy, elle est remplacée par le chant Maréchal, nous voilà4 ! En zone occupée, le commandement militaire allemand interdit de la jouer et de la chanter à partir du 17 juillet 19415.\nSon caractère d’hymne national est à nouveau affirmé dans l’article 2 de la Constitution du 27 octobre 1946 par la IVe République, et en 1958  par l’article 2 de la Constitution de la Cinquième République française.\nValéry Giscard d'Estaing, sous son mandat de président de la République française, fait ralentir le tempo de La Marseillaise afin de retrouver le rythme originel. Selon Guillaume Mazeau, la motivation était aussi « qu'elle ressemble moins à une marche militaire » hÃ© !""",
        ],
    ),
    "russian": (
        [
            "KOI8-R",
            "MacCyrillic",
            "IBM855",
            "IBM866",
            "iso8859_5",
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
    "traditional_chinese": (["utf_16_le", "utf_16_be", "utf_32_le", "utf_32_be"], []),
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
            "iso8859_2",
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
            "iso8859_5",
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
            "iso8859_7",
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


def getFileEncodingDetectFonction(bytes_, return_decoded=True):
    with open("test.txt", "wb") as f:
        f.write(bytes_)
    encoding = getFileEncoding("test.txt")
    with open("test.txt", "r", encoding=encoding, newline="") as f:
        decoded = f.read()
    if return_decoded:
        return encoding, decoded
    else:
        return encoding


# tests avec encodage dans un bytes ------------------
for detectFonction in (
    getEncoding,
    getFileEncodingDetectFonction,
):  # chardet.detect,cchardet.detect:# :# :
    print(
        "\n%s.%s ---------------------"
        % (detectFonction.__module__, detectFonction.__name__)
    )
    tests = 0
    start = perf_counter()
    errors = 0
    succed = 0
    for encodings, strings in encodings_strings_from_language.values():
        for string in strings:
            bytes_already_tested_for_this_string = set()
            for encoding in encodings:
                encoding = normalizeEncoding(encoding)
                try:
                    bytes_ = string.encode(encoding)
                except:
                    continue
                if bytes_ in bytes_already_tested_for_this_string:
                    continue
                tests += 1
                bytes_already_tested_for_this_string.add(bytes_)
                error = False
                if detectFonction in (getEncoding, getFileEncodingDetectFonction):
                    encoding_detected, decoded = detectFonction(
                        bytes_, return_decoded=True
                    )
                # print(detect)
                else:
                    encoding_detected = detectFonction(bytes_)
                    encoding_detected = encoding_detected["encoding"]
                    if encoding_detected is not None:
                        try:
                            decoded = bytes_.decode(encoding_detected)
                        except:
                            decoded = "ERROR"
                            error = True
                            errors += 1
                    else:
                        decoded = "No encoding detected"
                if (
                    detectFonction in (getEncoding, getFileEncodingDetectFonction)
                    or error
                ):
                    if string != decoded:
                        print(
                            repr(string)[1:-1],
                            "->",
                            repr(decoded)[1:-1],
                            "\t",
                            encoding,
                            "->",
                            encoding_detected,
                        )  #'->',bytes_,',assciPartIsPrintable(decoded)
                    elif encoding != encoding_detected and encoding_detected != "ascii":
                        print(
                            repr(string)[1:-1], "\t", encoding, "->", encoding_detected
                        )  #'->',bytes_,',assciPartIsPrintable(decoded)
                if string == decoded:
                    succed += 1

    end = perf_counter()
    succed_percent = 100 * succed / tests

    if errors:
        error_percent = 100 * errors / tests
        pass
        print(
            "succed {:.6f}% ERROR {:.6f}% in {:.4f}msec".format(
                succed_percent, error_percent, (end - start) * 1000
            )
        )
    else:
        print(
            "succed {:.6f}% in {:.4f}msec".format(succed_percent, (end - start) * 1000)
        )
