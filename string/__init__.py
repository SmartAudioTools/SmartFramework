# -*- coding: utf-8 -*-
from difflib import SequenceMatcher
import unicodedata
import re
import string
import os
import codecs
import locale
import cchardet
from encodings.aliases import aliases
import numpy
from rapidjson import load
from SmartFramework.string.romanNumber import isRoman
from SmartFramework.string.encodings import (
    cp1252_usuals,
    cp1252_usuals_mixed_utf_8,
    cp1252_printables,
    cp1252_french,
    cp1252_utf_8_keyboard_accessible,
    cp1252_mixed_utf_8,
)
from functools import lru_cache
from dateutil.parser import parse


with open(os.path.dirname(__file__) + "/stopwords.json", "rb") as stopwordsFile:
    stopwords = load(stopwordsFile)


def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


# https://www.rapidtables.com/web/color/RGB_Color.html
no_color = "\033[0m"
maroon = rgb(128, 0, 0)
dark_red = rgb(139, 0, 0)
brown = rgb(165, 42, 42)
firebrick = rgb(178, 34, 34)
crimson = rgb(220, 20, 60)
red = rgb(255, 0, 0)
tomato = rgb(255, 99, 71)
coral = rgb(255, 127, 80)
indian_red = rgb(205, 92, 92)
light_coral = rgb(240, 128, 128)
dark_salmon = rgb(233, 150, 122)
salmon = rgb(250, 128, 114)
light_salmon = rgb(255, 160, 122)
orange_red = rgb(255, 69, 0)
dark_orange = rgb(255, 140, 0)
orange = rgb(255, 165, 0)
gold = rgb(255, 215, 0)
dark_golden_rod = rgb(184, 134, 11)
golden_rod = rgb(218, 165, 32)
pale_golden_rod = rgb(238, 232, 170)
dark_khaki = rgb(189, 183, 107)
khaki = rgb(240, 230, 140)
olive = rgb(128, 128, 0)
yellow = rgb(255, 255, 0)
yellow_green = rgb(154, 205, 50)
dark_olive_green = rgb(85, 107, 47)
olive_drab = rgb(107, 142, 35)
lawn_green = rgb(124, 252, 0)
chart_reuse = rgb(127, 255, 0)
green_yellow = rgb(173, 255, 47)
dark_green = rgb(0, 100, 0)
green = rgb(0, 128, 0)
forest_green = rgb(34, 139, 34)
lime = rgb(0, 255, 0)
lime_green = rgb(50, 205, 50)
light_green = rgb(144, 238, 144)
pale_green = rgb(152, 251, 152)
dark_sea_green = rgb(143, 188, 143)
medium_spring_green = rgb(0, 250, 154)
spring_green = rgb(0, 255, 127)
sea_green = rgb(46, 139, 87)
medium_aqua_marine = rgb(102, 205, 170)
medium_sea_green = rgb(60, 179, 113)
light_sea_green = rgb(32, 178, 170)
dark_slate_gray = rgb(47, 79, 79)
teal = rgb(0, 128, 128)
dark_cyan = rgb(0, 139, 139)
aqua = rgb(0, 255, 255)
cyan = rgb(0, 255, 255)
light_cyan = rgb(224, 255, 255)
dark_turquoise = rgb(0, 206, 209)
turquoise = rgb(64, 224, 208)
medium_turquoise = rgb(72, 209, 204)
pale_turquoise = rgb(175, 238, 238)
aqua_marine = rgb(127, 255, 212)
powder_blue = rgb(176, 224, 230)
cadet_blue = rgb(95, 158, 160)
steel_blue = rgb(70, 130, 180)
corn_flower_blue = rgb(100, 149, 237)
deep_sky_blue = rgb(0, 191, 255)
dodger_blue = rgb(30, 144, 255)
light_blue = rgb(173, 216, 230)
sky_blue = rgb(135, 206, 235)
light_sky_blue = rgb(135, 206, 250)
midnight_blue = rgb(25, 25, 112)
navy = rgb(0, 0, 128)
dark_blue = rgb(0, 0, 139)
medium_blue = rgb(0, 0, 205)
blue = rgb(0, 0, 255)
royal_blue = rgb(65, 105, 225)
blue_violet = rgb(138, 43, 226)
indigo = rgb(75, 0, 130)
dark_slate_blue = rgb(72, 61, 139)
slate_blue = rgb(106, 90, 205)
medium_slate_blue = rgb(123, 104, 238)
medium_purple = rgb(147, 112, 219)
dark_magenta = rgb(139, 0, 139)
dark_violet = rgb(148, 0, 211)
dark_orchid = rgb(153, 50, 204)
medium_orchid = rgb(186, 85, 211)
purple = rgb(128, 0, 128)
thistle = rgb(216, 191, 216)
plum = rgb(221, 160, 221)
violet = rgb(238, 130, 238)
magenta = fuchsia = rgb(255, 0, 255)
orchid = rgb(218, 112, 214)
medium_violet_red = rgb(199, 21, 133)
pale_violet_red = rgb(219, 112, 147)
deep_pink = rgb(255, 20, 147)
hot_pink = rgb(255, 105, 180)
light_pink = rgb(255, 182, 193)
pink = rgb(255, 192, 203)
antique_white = rgb(250, 235, 215)
beige = rgb(245, 245, 220)
bisque = rgb(255, 228, 196)
blanched_almond = rgb(255, 235, 205)
wheat = rgb(245, 222, 179)
corn_silk = rgb(255, 248, 220)
lemon_chiffon = rgb(255, 250, 205)
light_golden_rod_yellow = rgb(250, 250, 210)
light_yellow = rgb(255, 255, 224)
saddle_brown = rgb(139, 69, 19)
sienna = rgb(160, 82, 45)
chocolate = rgb(210, 105, 30)
peru = rgb(205, 133, 63)
sandy_brown = rgb(244, 164, 96)
burly_wood = rgb(222, 184, 135)
tan = rgb(210, 180, 140)
rosy_brown = rgb(188, 143, 143)
moccasin = rgb(255, 228, 181)
navajo_white = rgb(255, 222, 173)
peach_puff = rgb(255, 218, 185)
misty_rose = rgb(255, 228, 225)
lavender_blush = rgb(255, 240, 245)
linen = rgb(250, 240, 230)
old_lace = rgb(253, 245, 230)
papaya_whip = rgb(255, 239, 213)
sea_shell = rgb(255, 245, 238)
mint_cream = rgb(245, 255, 250)
slate_gray = rgb(112, 128, 144)
light_slate_gray = rgb(119, 136, 153)
light_steel_blue = rgb(176, 196, 222)
lavender = rgb(230, 230, 250)
floral_white = rgb(255, 250, 240)
alice_blue = rgb(240, 248, 255)
ghost_white = rgb(248, 248, 255)
honeydew = rgb(240, 255, 240)
ivory = rgb(255, 255, 240)
azure = rgb(240, 255, 255)
snow = rgb(255, 250, 250)
black = rgb(0, 0, 0)
dim_gray = dim_grey = rgb(105, 105, 105)
gray = grey = rgb(128, 128, 128)
dark_gray = dark_grey = rgb(169, 169, 169)
silver = rgb(192, 192, 192)
light_gray = light_grey = rgb(211, 211, 211)
gainsboro = rgb(220, 220, 220)
white_smoke = rgb(245, 245, 245)
white = rgb(255, 255, 255)


class ENCODING________________________________________________:
    pass


# encodings ----------
local_encoding = locale.getdefaultlocale()[1]
encodings_with_ascii_subset = [
    "ascii",
    "big5",
    "big5hkscs",
    "cp1006",
    "cp1125",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "cp437",
    "cp65001",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp932",
    "cp949",
    "cp950",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_jp",
    "euc_kr",
    "gb18030",
    "gb2312",
    "gbk",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso8859_10",
    "iso8859_11",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "johab",
    "koi8_r",
    "koi8_t",
    "koi8_u",
    "kz1048",
    "latin_1",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "utf_8",
    "utf_8_sig",
]
encodings_not_8bit = [
    "iso2022_jp",
    "iso8859_5",
    "iso2022_kr",
    "euc_jp",
    "shift_jis",
    "big5",
    "gb2312",
    "gb18030",
    "hz",
    "koi8_r",
    "mac_cyrillic",
    "cp855",
    "cp866",
    "cp1251",
    "euc_kr",
    "utf_7",
]
BOMS = {
    "utf_8_sig": codecs.BOM_UTF8,
    "utf_32": codecs.BOM_UTF32,
    "utf_16": codecs.BOM_UTF16,
}


def decode(
    bytes_, encoding=None, encodings=False, replace_newline=False, return_encoding=False
):
    replace_r_after_decoding = False
    if replace_newline:
        if (
            b"\r" in bytes_
        ):  # permet de gerer melange de \r\n et de \n , par contre va foirer si fichier mac avant OSX
            if b"\x00" in bytes_:
                replace_r_after_decoding = (
                    True  # pour ne pas foutre en l'air UTF16 ou UTF32 si présence de \r
                )
            else:
                bytes_ = bytes_.replace(b"\r", "")
    if encoding:
        decoded = bytes_.decode(encoding)
    else:
        encoding, decoded = getEncoding(
            bytes_, encodings=encodings, return_decoded=True
        )
    if replace_r_after_decoding:
        decoded = decoded.replace(b"\r", "")
    if return_encoding:
        return decoded, encoding
    return decoded


def getNewline(bytes_or_string):
    """detecte le type du dernier newline
    ne veut pas dire qu'il n'y a qu'un type de newline...
    """
    if isinstance(bytes_or_string, str):
        last_backslash_n = bytes_or_string.rfind("\n")
        if last_backslash_n > 0:
            if bytes_or_string[last_backslash_n - 1] == "\r":
                return "\r\n"
        elif "\r" in bytes_or_string:  # versions Mac avant OS X
            return "\r"
        return "\n"
    else:
        last_backslash_n = bytes_or_string.rfind(b"\n")
        if last_backslash_n > 0:
            if bytes_or_string[last_backslash_n - 1] == 13:
                return b"\r\n"
        elif b"\r" in bytes_or_string:  # versions Mac avant OS X
            return b"\r"
        return b"\n"


# @profile
def getEncoding(bytes_, encodings=None, return_decoded=False):
    if encodings is None:
        encodings = [
            "ascii",
            "utf_8",
            "cp1252",
            "cp1252_mixed_utf8",
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
    chardet_confidence_threshold = (
        0.8  # pour ne pas merder sur les mot de 3 lettre aléatoires
    )
    enable_cp1252_mixed_utf_8 = "cp1252_mixed_utf8" in encodings
    detect_utf16_utf32 = ("utf_16" in encodings) or ("utf_32" in encodings)
    for enc in encodings:
        if enc in encodings_with_ascii_subset:
            encoding_if_ascii = enc
            break
    else:
        encoding_if_ascii = "ascii"

    decoded = None

    # test BOM -------------------------------------------------------------------
    for (
        encoding,
        bom,
    ) in (
        BOMS.items()
    ):  # attention en théorie en debut de fichier , pas sur que ce soit partinent de le detecter dans un bytes quelconque
        if bytes_.startswith(bom):
            if return_decoded:
                decoded = bytes_.decode(encoding)
                return encoding, decoded
            else:
                return encoding
    encoding = None

    bytes_isascii = bytes_.isascii()
    bytes_len = len(bytes_)

    # cas particulier un seul caractère (vraiment utile ? )
    if bytes_len == 1:
        if bytes_isascii:
            encoding = "ascii"
        else:
            try:
                bytes_.decode("cp1252_printables")
                encoding = "cp1252"
            except:
                try:
                    bytes_.decode(local_encoding)
                    encoding = local_encoding
                except:
                    encoding = "cp1252"

    # teste utf_8 -------------------------------------------------------------
    if (
        not bytes_isascii
    ):  # plus besoin de tester ascii ,on va faire des teste pour tenter de deviner l'encoding entre 'utf_8',local_encoding et ainsi avoir plus de chance de tenter directemetn le bon décoding .
        test_utf_8 = True
        should_check_if_not_cp1252 = False  # pour cas particulier 'é€€'
        if (
            195 not in bytes_
        ):  # si 'Ã' était présent dans le bytes -> très forte chance que ce soit du l'utf_8, on va directement le tester,  mais malheureusment on ne peut pas en être certain sans tester ... ce test est utile pour eviter de scanner si dessous toute la string à       #la recherche de 233, alors qu'il est plus probable que ce soit de l'utf_8 que du cp1252,de plus meme s'il avaient la même probablité, 195 permet de détececter un plsuieus caractère avec accent et sera  plus vite détécté que 233 qui ne teste que le "é" en cp1252
            should_check_if_not_cp1252 = True
            index_é = bytes_.find(
                233
            )  # 'é' présent de le bytes, qui est le caractère le plus fréquent en francais à ne pas être décodable en utf_8 quand encodé en cp1252 (https://fr.wikipedia.org/wiki/Fréquence_d'apparition_des_lettres_en_français) mais peut tout de même être de l'utf_8 si suivit de deux octets compris entre 128 et 191 deffinisent aussi avec eux un caractère utf_8 chinois ()
            if 0 <= index_é and (
                index_é == bytes_len - 1 or not (128 <= bytes_[index_é + 1] <= 191)
            ):  # ce n'est pas un caractère chinois en utf_8
                test_utf_8 = False  # on ne teste meme pas l'utf_8
        if test_utf_8:
            try:
                decoded = bytes_.decode("utf_8")
                encoding = "utf_8"
            except:
                pass
            else:
                # vraiment utile ???   gère le cas particulier de chaines cp1252 avec que des caractère tapable avec un clavier qui par le plus grand des hasard (on de façon déliberé pour tromper l'algo)  se décode en utf-8 ex: "j'ai plein de blé€€" ou "Â€"
                if should_check_if_not_cp1252:
                    try:
                        decoded = bytes_.decode("cp1252_utf_8_keyboard_accessible")
                        encoding = "cp1252"
                    except:
                        pass

    # Test others encoding ----------------------------------------------------
    if encoding is None:
        if only_utf_8_cp1252_local:
            if bytes_isascii:  # asssume it is "ascii"
                encoding = "ascii"
            elif local_encoding == "cp1252":
                encoding = "cp1252"  # asssume "cp1252"
            else:
                result = cchardet.detect(bytes_)
                chardet_encoding = normalizeEncoding(result["encoding"])
                if chardet_encoding == "latin_1":
                    chardet_encoding = "cp1252"
                if chardet_encoding == local_encoding:
                    encoding = local_encoding
                else:
                    encoding = "cp1252"

        # searh others codecs with chardet ------------------------------------
        else:
            result = cchardet.detect(bytes_)
            chardet_confidence = result["confidence"]
            chardet_encoding = normalizeEncoding(
                result["encoding"]
            )  # attention si on le remonte , ça peut être None
            if chardet_encoding == "latin_1":
                chardet_encoding = "cp1252"
            if (
                chardet_confidence is not None
                and chardet_confidence > chardet_confidence_threshold
            ):
                if chardet_encoding not in (
                    "utf_8",
                    "ascii",
                ):  # si utf-8 ne serai pas là , si 'ascii' ca peut être de utf_16_le ou utf_16_be
                    try:
                        decoded = bytes_.decode(
                            chardet_encoding
                        )  # verifie que ça passe pas toujours le cas pour ensemble de 3 lettres
                        encoding = chardet_encoding
                    except:
                        pass
                    else:
                        pass
                        if (
                            enable_cp1252_mixed_utf_8 and 195 in bytes_
                        ):  # and chardet_encoding in ( 'utf_8', 'cp1252') :
                            try:
                                decoded = bytes_.decode("cp1252_usuals_mixed_utf_8")
                                encoding = "cp1252_mixed_utf_8"
                            except:
                                pass
                        # sert uniqument à resorir le bon nom 'cp1252' , meme si meme resultat
                        # le dégage car trop compliqué à implémnter dans getFileEncoding hors on veut le meme resultat
                        # if chardet_encoding  != 'cp1252' :
                        #    try :
                        #         decoded_cp1252 = bytes_.decode('cp1252')
                        #         if decoded_cp1252 == decoded :
                        #             encoding = 'cp1252'
                        #    except :
                        #         pass

            # chardet n'est pas sûre de lui -> tente avec cp1252 restreint au caractères usuels -----

            if encoding is None:
                try:
                    decoded = bytes_.decode("cp1252_usuals")
                    if bytes_isascii:
                        encoding = encoding_if_ascii
                    else:
                        encoding = "cp1252"
                except:
                    pass

            if encoding is None:
                if (
                    enable_cp1252_mixed_utf_8 and 195 in bytes_
                ):  # and chardet_encoding in ( 'utf_8', 'cp1252') :
                    try:
                        decoded = bytes_.decode("cp1252_usuals_mixed_utf_8")
                        encoding = "cp1252_mixed_utf_8"
                    except:
                        pass

                if encoding is None:
                    to_try_after = []
                    if chardet_confidence is not None and chardet_encoding not in (
                        "utf_8",
                        "ascii",
                    ):  # sinon on serait pas là
                        if chardet_confidence > 0.55:
                            try:
                                decoded = bytes_.decode(
                                    chardet_encoding
                                )  # verifie que ça passe pas toujours le cas pour ensemble de 3 lettres
                                encoding = chardet_encoding
                            except:
                                pass
                        else:
                            to_try_after = [chardet_encoding]

                    # ne semble pas etre du cp1252 -> try others not 8 bit encodings on aproximatively first 100 chars  ---------------------------------

                    # ('utf_16_be','utf_16_le','utf_32_be','utf_32_le','utf_7' and others)

                    if encoding is None:
                        if detect_utf16_utf32 and bytes_len % 2 == 0:
                            first_space = bytes_.find(b" ")
                            if first_space != -1:
                                first_space_or_line_feed = first_space
                            else:
                                first_space_or_line_feed = bytes_.find(b"\n")
                            if first_space_or_line_feed != -1:
                                if first_space_or_line_feed % 2:
                                    if bytes_[first_space_or_line_feed - 1] == 0:
                                        if (
                                            first_space_or_line_feed >= 3
                                            and bytes_[first_space_or_line_feed - 2]
                                            == 0
                                            and bytes_[first_space_or_line_feed - 2]
                                            == 0
                                        ):
                                            encoding = "utf_32_be"
                                        else:
                                            encoding = "utf_16_be"
                                else:
                                    if (
                                        first_space_or_line_feed + 1 < bytes_len
                                        and bytes_[first_space_or_line_feed + 1] == 0
                                    ):
                                        if (
                                            first_space_or_line_feed + 3 < bytes_len
                                            and bytes_[first_space_or_line_feed + 2]
                                            == 0
                                            and bytes_[first_space_or_line_feed + 3]
                                            == 0
                                        ):
                                            encoding = "utf_32_le"
                                        else:
                                            encoding = "utf_16_le"

                        if encoding is None:
                            if detect_utf16_utf32 and bytes_len % 2 == 0:
                                if b"\x00" in bytes_:
                                    to_try_after = [
                                        "utf_16_be",
                                        "utf_16_le",
                                        "utf_32_be",
                                        "utf_32_le",
                                    ]
                                else:
                                    to_try_after = (
                                        to_try_after
                                        + encodings_not_8bit
                                        + [
                                            "utf_16_be",
                                            "utf_16_le",
                                            "utf_32_be",
                                            "utf_32_le",
                                        ]
                                    )
                            else:
                                to_try_after = to_try_after + encodings_not_8bit

                            if encoding is None:
                                first_bytes = bytes_
                                full = True
                                next_line_feed = bytes_.find(b"\n", 100)
                                if next_line_feed != -1:
                                    first_bytes = bytes_[:next_line_feed]
                                    full = False
                                encoding = _findBestEncoding(
                                    first_bytes, to_try_after, full=full
                                )

                                # no codec was found, take ascii or local_encoding -----------------
                                # pas sûr qu'on puisse arriver ici si _findBestEncoding retourne de toute facon quelque chose
                                if encoding is None:
                                    if bytes_isascii:
                                        encoding = "ascii"
                                    else:
                                        encoding = local_encoding

    if return_decoded:
        if decoded is None:
            decoded = bytes_.decode(encoding)
        if encoding == "ascii":
            return (
                encoding_if_ascii,
                decoded,
            )  # mis aprs le bytes_.decode(encoding) pour ne pas le ralentir ?
        return encoding, decoded
    else:
        if encoding == "ascii":
            return encoding_if_ascii
        return encoding


def encodingWithoutBom(encoding):
    encoding = normalizeEncoding(encoding)
    if encoding == "utf_8_sig":
        return "utf_8"
    elif encoding == "utf_16":
        return "utf_16_le"
    elif encoding == "utf_32":
        return "utf_32_le"
    else:
        return encoding


def normalizeEncoding(encoding):
    """used for normalize cchardet result encoding
    modified https://github.com/python/cpython/blob/master/Lib/encodings/__init__.py"""
    if encoding is None:
        return None
    if isinstance(encoding, bytes):
        encoding = str(encoding, "ascii")
    encoding = encoding.lower()
    chars = []
    punct = False
    for c in encoding:
        if c.isalnum() or c == ".":
            if punct and chars:
                chars.append("_")
            chars.append(c)
            punct = False
        else:
            punct = True
    encoding_lower_underscored = "".join(chars)
    return aliases.get(encoding_lower_underscored, encoding_lower_underscored)


def _findBestEncoding(bytes_, encodings, full=True):
    best_len_decoded = 9223372036854775807  # sys. maxsize
    best_standard_deviation = 9223372036854775807  # sys. maxsize
    best_encoding = None
    best_local_ratio = -1
    for enc in encodings:
        """if not full:
        if enc == "utf_32_be" :
            mod_4 = len(bytes_)%4
            if mod_4 != 0  :
                bytes_test = bytes_[:-mod_4]
        elif enc == "utf_16_be" :
            mod_2 = len(bytes_)%2
            if mod_2 != 0  :
                bytes_test = bytes_[:-mod_2]
        else :
            bytes_test = bytes_"""
        try:
            decoded = bytes_.decode(enc)
        except:
            continue
        else:
            len_decoded = len(decoded)
            if not len_decoded:
                continue
            repr_decoded = repr(decoded)
            if (
                "\\u" in decoded or "\\u" not in repr_decoded
            ):  # tout les caractère sont printables ou ascii, le and not "x" in repr_decode  empèche de detecter un "à".encode("utf-8").decode("cp1252").encode("utf_16_be") comme étant du utf_16_be
                # if "\\x" in repr(decoded) :
                if (
                    len_decoded <= best_len_decoded
                ):  # len(decoded)<= best_len and len(decoded) +2 == len(repr(decoded)):
                    for (
                        c
                    ) in "\x00\x01\x02\x03\x04\x05\x06\x07\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f":  # caractère ascii non printables
                        if c in decoded:
                            break
                    else:
                        # cp1252_usuals_chars = decoded.encode('cp1252_usuals','ignore') #2x plus long...
                        # local_ratio =  len(cp1252_usuals_chars)/len(decoded)
                        not_local = decoded.translate(remove_ordinary_chars_tanslator)
                        local_ratio = 1.0 - len(not_local) / len(decoded)
                        if (
                            len_decoded < best_len_decoded
                            or local_ratio >= best_local_ratio
                        ):

                            if enc in (
                                "utf_16_be",
                                "utf_16_le",
                                "utf_32_be",
                                "utf_32_le",
                            ):
                                # standard_deviation = numpy.std(numpy.fromiter((ord(c) for c in decoded),dtype = int,count = len(decoded))) # utilie pour lever ambiguité pour entre utf_16_be vs utf_16_le
                                try:
                                    decoded.encode("cp1252_printables")
                                    return enc
                                    # standard_deviation = 0
                                except:
                                    pass
                                    if len(decoded) > 1:
                                        standard_deviation = numpy.std(
                                            [ord(c) for c in decoded]
                                        )
                                    else:
                                        standard_deviation = ord(decoded)
                            else:
                                standard_deviation = 0

                            if (
                                len_decoded < best_len_decoded
                                or local_ratio > best_local_ratio
                                or standard_deviation < best_standard_deviation
                            ):
                                best_standard_deviation = standard_deviation
                                best_local_ratio = local_ratio
                                best_len_decoded = len_decoded
                                best_encoding = enc
    return best_encoding


class TRANSFORM________________________________________________:
    pass


# translators --------
remove_ordinary_chars_tanslator = str.maketrans(
    "",
    "",
    """\t\n\r !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{}~€£µàâæçèéêëîïòóôöùúû""",
)


def capitalizeFirstLetter(string):
    if len(string) > 1:
        return string[0].upper() + string[1:]
    elif len(string):
        return string.upper()
    return string


def capitalize(name, language="fr", upToLower=True, stopwordsLow=True):
    # decoupe en liste de listes
    words = []
    wordL = []
    wordsAndSpliters = []
    for i, c in enumerate(name):
        if c in """()[]._-, '_#-!"&@}^\`|{~=:;+/?`$*%""":
            if wordL:
                words.append(wordL)
                wordsAndSpliters.append(wordL)
                wordL = []
            wordsAndSpliters.append(c)
        else:
            wordL.append(c)
    if wordL:
        words.append(wordL)
        wordsAndSpliters.append(wordL)
    # travaile dessus

    for wordL in words:
        if stopwordsLow and "".join(wordL) in stopwords[language]:
            for i, c in enumerate(wordL):
                wordL[i] = c.lower()
        else:
            for i, c in enumerate(wordL):
                if i == 0:
                    wordL[i] = c.upper()
                elif upToLower:
                    wordL[i] = c.lower()
    return "".join([c for wordOrSpliter in wordsAndSpliters for c in wordOrSpliter])


def smartTitle(s):
    champs = s.split(" ")
    newChamps = []
    for i, champ in enumerate(champs):
        if isRoman(champ):
            newChamps.append(champ.upper())
        else:
            newChamps.append(champ.title())
    return " ".join(newChamps)


def toASCII(s):
    # rajouté  .replace(u"\u2018", "'").replace(u"\u2019", "'") pour gerer title de http://www.france24.com/fr/20150109-charlie-hebdo-je-ne-suis-pas-charlie-contestation-emotion-france-attentat-journlaistes-liberte-expression/
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def vireAccentEtMajuscules(s):
    return (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )


ascii_lower = vireAccentEtMajuscules


def ascii_lower_strip(s):
    return (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


def normalize(s):
    s = vireAccentEtMajuscules(s)
    s = removeStrangeCharacter(s)
    return s


def removeStrangeCharacter(st):
    for c in "_#-)!('\"&@}]^\`|[{~=:;,+/.?`$*%":
        st = st.replace(c, " ")
        st = st.replace("  ", " ")
    st = st.strip()
    return st


def multiReplace(text, replaceDict):
    # use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in replaceDict.items())
    pattern = re.compile("|".join(list(rep.keys())))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text


def toValidVarname(varStr):
    return re.sub("\W|^(?=\d)", "_", varStr)


def toValidPath(path):
    """
    Normalizes string, removes non-alpha characters
    """
    path = unicodedata.normalize("NFKD", path)
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return "".join(char for char in path if char in valid_chars)


class LIST_OF_STRINGS________________________________________________:
    pass


def spliter(s, spliters="()[]._-, '"):
    for c in spliters:
        s = s.replace(c, "/")
    champs = [x for x in s.split("/") if x != ""]
    return champs


def addNewlines(lines, newline="\n"):
    if isinstance(lines, (str, bytes)):
        lines = [lines]
    if newline:
        first = True
        prior_line = None
        for line in lines:
            if first:
                first = False
                if isinstance(line, bytes) and isinstance(newline, str):
                    newline = newline.encode("ascii")
            else:
                yield prior_line
                yield newline
            prior_line = line
        if prior_line is not None:
            yield prior_line
        else:
            return
    else:
        for line in lines:
            yield line


class ANALYZE________________________________________________:
    pass


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def extract(line, before, after):
    beforeIndex = line.find(before)
    if beforeIndex != -1:
        startIndex = beforeIndex + len(before)
        endIndex = line.find(after, startIndex)
        return line[startIndex:endIndex]
    else:

        return None


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


class Match:
    def __init__(self, language="fr"):
        self.phrases = None
        self.normalizedToPhrases = {}
        self.language = language

    def cleanedNormalizedAndWords(self, st, language=None):
        if language is None:
            language = self.language
        cleanedWords = set()
        cleanedWords_with_stopwords = set()
        normalized = normalize(st)
        for word in normalize(st).split(" "):
            cleanedWords_with_stopwords.add(word)
            if word not in stopwords[self.language]:
                cleanedWords.add(word)
        if len(cleanedWords) == 0:
            cleanedWords = cleanedWords_with_stopwords
        return normalized, cleanedWords

    def setPhrases(self, phrases, language=None):
        self.normalizedToPhrases = {}
        if language is None:
            language = self.language
        if phrases != self.phrases:
            phraseToWords = dict()
            for testPhrase in phrases:
                (
                    normalizedPhrase,
                    phraseToWords[testPhrase],
                ) = self.cleanedNormalizedAndWords(testPhrase)
                self.normalizedToPhrases[normalizedPhrase] = testPhrase
            self.phraseToWords = phraseToWords
            self.phrases = phrases

    @lru_cache(maxsize=1000)
    def bestMatching(
        self,
        phrase,
        phrases=None,
        thresold=0.0,
        useSimilarity=True,
        printNoMatch=True,
        printHesitation=True,
        printRecognized=False,
    ):
        if phrases is not None:
            self.setPhrases(phrases)
        normalized, words = self.cleanedNormalizedAndWords(phrase)
        bingo = self.normalizedToPhrases.get(normalized, None)
        if bingo is not None:
            return bingo
        len_words = len(words)
        bestNote = -(2**31)  # min int32
        bestPhrases = set()
        for testPhrase, testWords in self.phraseToWords.items():
            note = 0
            if not useSimilarity:
                # simple comparaison (saut faute d'ortographes)
                communWords = testWords & words
                note = len(communWords) * 3 - len_words
            else:
                # se permet des fautes d'orthographe
                foundWords = set()
                for word in words:
                    if word in testWords:
                        note += 1
                    else:
                        bestSim = -(2**31)
                        for testWord in testWords:
                            sim = similarity(word, testWord)
                            if sim > bestSim:
                                bestWord = testWord
                                bestSim = sim
                        if bestSim > 1 - (1 / (max(len(word), len(bestWord)))):
                            note += 2 * bestSim - 1
                            foundWords.add(bestWord)
                        else:
                            note -= 2
                    note -= 0.1 * len(
                        testWords - foundWords
                    )  # pénalise un peu les mots qu'il n'a pas trouvé
            if note / len(words) >= thresold:
                if note > bestNote:
                    bestPhrases = set([testPhrase])
                    bestNote = note
                elif note == bestNote:
                    bestPhrases.add(testPhrase)
        len_bestPhrases = len(bestPhrases)
        if len_bestPhrases == 0:
            if printNoMatch:
                print('Impossible de retrouver "{}"'.format(phrase))
            return None
        elif len_bestPhrases == 1:
            bestPhrase = list(bestPhrases)[0]
            if printRecognized:
                print('reconnait "{}" dans "{}"'.format(phrase, bestPhrase))
            return bestPhrase
        else:
            if printHesitation:
                print(
                    'Hesite pour  "{}" entre :\n. "{}"'.format(
                        phrase, '"\n. "'.join(list(bestPhrases))
                    )
                )
            return bestPhrases
