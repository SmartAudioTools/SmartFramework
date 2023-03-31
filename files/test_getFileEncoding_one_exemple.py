# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 16:10:41 2020

@author: Baptiste
"""
# from SmartFramework.string import getEncoding,_assciPartIsPrintable
from SmartFramework.files import getFileEncoding, read

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
# string = "hÃ©!\nbonjour\nvous Ãªtes prÃªts Ã\xa0 partir dans les pr\\Ã¨s ?\nnmoi j'ai mangé"; encoding = 'cp1252'
# string = "À"; encoding = 'utf_8'
# string = "salut les amis\ncomment ca va? je vais vous racompter une histoire , pour avoir beaucoups de caractères et  depasser les 100.\n ça me permet d'être sur que le utf_16_be passe bien\n C'est compris ?";encoding = "utf_16_le"
string = "hÃ©!\nbonjour\nvous Ãªtes prÃªts?\nmoi j'ai mangé "
encoding = "cp1252_mixed_utf_8"
# encoding = "cp1252"
# string = "¢"  # '''La Marseillaise est un chant patriotique de la Révolution française adopté par la France comme hymne national : une première fois par la Convention pendant neuf ans du 14 juillet 1795 jusqu'à l'Empire en 1804, puis en 1879 sous la Troisième République1.\nLes six premiers couplets sont écrits par Rouget de Lisle2 sous le titre de Chant de guerre pour l'armée du Rhin3 en 1792 pour l'armée du Rhin à Strasbourg, à la suite de la déclaration de guerre de la France à l'Autriche. Dans ce contexte originel, La Marseillaise est un chant de guerre révolutionnaire, un hymne à la liberté, un appel patriotique à la mobilisation générale et une exhortation au combat contre la tyrannie et l'invasion étrangère.\nLa Marseillaise est décrétée chant national le 14 juillet 1795 (26 messidor an III) par la Convention, à l'initiative du Comité de salut public. Abandonnée en 1804 sous l’Empire et remplacée par le Chant du départ, elle est reprise en 1830 pendant la révolution des Trois Glorieuses qui porte Louis-Philippe Ier au pouvoir. Berlioz en élabore une orchestration qu’il dédie à Rouget de Lisle. Mais Louis-Philippe impose La Parisienne, chant plus modéré. La Marseillaise est de nouveau interdite sous le second Empire3.\nLa IIIe République en fait l'hymne national le 14 février 1879 et, en 1887, une « version officielle » est adoptée en prévision de la célébration du centenaire de la Révolution.\nLe 14 juillet 1915, les cendres de Rouget de Lisle sont transférées aux Invalides.\nPendant la période du régime de Vichy, elle est remplacée par le chant Maréchal, nous voilà4 ! En zone occupée, le commandement militaire allemand interdit de la jouer et de la chanter à partir du 17 juillet 19415.\nSon caractère d’hymne national est à nouveau affirmé dans l’article 2 de la Constitution du 27 octobre 1946 par la IVe République, et en 1958  par l’article 2 de la Constitution de la Cinquième République française.\nValéry Giscard d'Estaing, sous son mandat de président de la République française, fait ralentir le tempo de La Marseillaise afin de retrouver le rythme originel. Selon Guillaume Mazeau, la motivation était aussi « qu'elle ressemble moins à une marche militaire » hÃ© !'''


bytes_ = string.encode(encoding)
with open("test.txt", "wb") as f:
    f.write(bytes_)
encoding_detected = getFileEncoding("test.txt")
# encoding_detected = getEncoding(bytes_)
decoded = read("test.txt", encoding=encoding_detected)


if string != decoded:
    # print(string,'('+encoding+')', '->', stringOut ,'('+encodingDetected+')','\t', )
    print(
        repr(string)[1:-1],
        "->",
        repr(decoded)[1:-1],
        "\t",
        encoding,
        "->",
        bytes_,
        "->",
        encoding_detected,
    )
elif encoding != encoding_detected:
    print(repr(string)[1:-1], "\t", encoding, "->", bytes_, "->", encoding_detected)
else:
    print("ok")
