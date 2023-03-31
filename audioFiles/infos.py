# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import os
import mutagen.id3
import mutagen.easyid3
import mutagen.asf
import mutagen.flac
from SmartFramework.files import ext, splitPath, name
from .translateToMainGenre import translateToMainGenre
from .translateToMyGenre import translateToMyGenre

nbTitlesFor3stars = 7

starsToMp3Rating = {1: 1, 2: 64, 3: 128, 4: 196, 5: 255}
mp3RatingToStars = {1: 1, 64: 2, 128: 3, 196: 4, 255: 5}
wmaRatingToStars = {1: 1, 25: 2, 50: 3, 75: 4, 99: 5}
starsToWmaRating = {1: 1, 2: 25, 3: 50, 4: 75, 5: 99}
starsToFlacRating = {1: 1, 2: 25, 3: 50, 4: 75, 5: 99}
starsToFlacRatingWmp = {1: 51, 2: 102, 3: 153, 4: 204, 5: 255}

commentSplit = "/"

wmaToMp3Tag = {
    "Author": "artist",
    "WM/ArtistSortOrder": "artistsort",
    "MusicBrainz/Artist Id": "musicbrainz_artistid",
    "WM/AlbumArtistSortOrder": "albumartistsort",
    "MusicBrainz/Album Artist Id": "musicbrainz_albumartistid",
    "WM/Genre": "genre",
    # album
    "WM/AlbumTitle": "album",
    "MusicBrainz/Album Id": "musicbrainz_albumid",
    "MusicBrainz/Album Type": "musicbrainz_albumtype",
    "MusicBrainz/Album Status": "musicbrainz_albumstatus",
    # track
    "Title": "title",
    "MusicBrainz/Track Id": "musicbrainz_trackid",
    "WM/TrackNumber": "tracknumber",
}
"""
     'WM/Year'                     : [ASFUnicodeAttribute(' ')],
     'WM/SharedUserRating'         : [ASFDWordAttribute(50)]
     'WM/Track': [ASFUnicodeAttribute('Cover You in Oil')],
     'WM/AlbumArtist'              : [ASFUnicodeAttribute('AC/DC')],

"""
keepedKeys = list(wmaToMp3Tag.values())


class Artist(object):
    def __init__(self, artist):
        self.artist = artist
        self.albums = dict()


class Album(object):
    def __init__(self, albumartist, album, path):
        self.albumartist = albumartist
        self.album = album
        self.path = path
        self.titleKeys = []

    def setTitlesDict(self, titlesDict):
        self._ALLfiles = titlesDict

    def getStars(self):
        nbNoted = 0
        bestStars = 0
        for titleKey in self.titleKeys:
            infos = self._ALLfiles[titleKey]
            if "stars" in infos:
                nbNoted += 1
                titleStars = infos["stars"]
                if titleStars > 2:
                    bestStars += titleStars - 2
        if bestStars == 0:
            stars = -1
        else:
            stars = min(int(3.0 * bestStars / (nbTitlesFor3stars)), 3)
        # if stars > 2 :
        #   print((self.path))
        return stars

    stars = property(getStars)

    def getRated(self):
        nbNoted = 0.0
        for titleKey in self.titleKeys:
            infos = self._ALLfiles[titleKey]
            if "stars" in infos:
                nbNoted += 1.0
        return nbNoted / len(self.titleKeys)

    rated = property(getRated)

    def getComplet(self):
        tracksInFolder = float(len(self.titleKeys))
        try:
            infos = self._ALLfiles[self.titleKeys[0]]
            tracksInALbum = float(infos["tracknumber"].split("/")[1])
            taux = min(tracksInFolder / tracksInALbum, 1.0)
            # print(taux)
        except:
            taux = None

        """
        complet = tracksInFolder / tracksInALbum
        if complet < 0.8:
            s = self.path + " : " + str(tracksInFolder) + "/" + str( tracksInALbum)
            print(s)
        """
        return taux

    complet = property(getComplet)


def alreadyCommented(comments, trueComment):
    return (trueComment in comments) or ("no " + trueComment in comments)


def addComment(path, addComment, infos=None, show=True, pause=False):

    if infos is not None:
        comments = infos.get("comments", [])
    else:
        infos = smartInfos(path)
        comments = infos.get("comments", [])

    save = False
    if addComment.startswith("no "):
        oppositeComment = addComment[3:]
    else:
        oppositeComment = "no " + addComment
    if oppositeComment in comments:
        comments.remove(oppositeComment)
        save = True
    if addComment not in comments:
        comments.append(addComment)
        save = True

    if save:
        if show:
            print(addComment + " -> " + name(path))
        if pause:
            os.system("pause")
        saveComments(path, comments)
        infos["comments"] = comments


def mp3Infos(path):
    # print('.',)
    try:
        easyId3 = mutagen.easyid3.EasyID3(path)
        id3v2 = easyId3._EasyID3__id3
        # id3v2 = mutagen.id3.ID3(path)

    except:
        print("impossible d'ouvrir ID3 de : " + path)
        os.system("pause")
        return None
    infos = {"paths": [path]}
    for key in easyId3.keys():
        if key in keepedKeys and len(easyId3[key]):
            infos[key] = easyId3[key][0]

    if "POPM:baptiste.delagorce@gmail.com" in id3v2:
        infos["stars"] = mp3RatingToStars[
            id3v2["POPM:baptiste.delagorce@gmail.com"].rating
        ]

    if "COMM::fre" in id3v2:
        infos["comments"] = id3v2["COMM::fre"].text[0].split(commentSplit)

    if "COMM::'fre'" in id3v2:
        infos["comments"] = id3v2["COMM::'fre'"].text[0].split(commentSplit)
        print("clef %s dans %s" % ("COMM::'fre'", path))
        """
        POPMs = id3v2.getall('POPM')
        if len(POPMs)>0 : 
            print(POPMs)
            mp3Rating = POPMs[0].rating
            stars = mp3RatingToStars[mp3Rating]
        """
    return infos


def saveComment(path, comment, lang="fre"):
    if ext(path) == "mp3":
        try:
            print(path)
            print(comment)
            # os.system('pause')
            id3v2 = mutagen.id3.ID3(path)
            COMMs = id3v2.getall("COMM")
            if len(COMMs) > 0:
                id3v2.delall("COMM")
            if comment:
                id3v2["COMM"] = mutagen.id3.COMM(
                    encoding=0, lang=lang, desc="", text=[comment]
                )
            id3v2.update_to_v23()
            id3v2.save(v2_version=3)
        except:
            print("ecriture imppossible")


def delComments(path):
    if ext(path) == "mp3":
        try:
            print(path)
            id3v2 = mutagen.id3.ID3(path)
            COMMs = id3v2.getall("COMM")
            if len(COMMs) > 0:
                id3v2.delall("COMM")
            id3v2.update_to_v23()
            id3v2.save(v2_version=3)
        except:
            print("ecriture imppossible")


def saveComments(path, comments, lang="fre"):
    if ext(path) == "mp3":
        # try :
        id3v2 = mutagen.id3.ID3(path)
        COMMs = id3v2.getall("COMM")
        if len(COMMs) > 0:
            id3v2.delall("COMM")
        if comments:
            id3v2["COMM"] = mutagen.id3.COMM(
                encoding=0, lang=lang, desc="", text=[commentSplit.join(comments)]
            )
        id3v2.update_to_v23()
        id3v2.save(v2_version=3)
        # except :
        #    print('ecriture imppossible')


def saveStars(path, stars, infos=None, pause=False):
    if pause:
        print("*" * stars + " " * (5 - stars) + " -> " + name(path))
    if infos is not None:
        infos["stars"] = stars
    if ext(path) == "mp3":
        id3v2 = mutagen.id3.ID3(path)
        POPMs = id3v2.getall("POPM")
        if len(POPMs) > 0:
            id3v2.delall("POPM")
        if stars:
            rating = starsToMp3Rating[stars]
            id3v2.add(
                mutagen.id3.POPM(
                    encoding=3, email=str("baptiste.delagorce@gmail.com"), rating=rating
                )
            )
        id3v2.update_to_v23()
        id3v2.save(v2_version=3)
    elif ext(path) == "wma":
        asf = mutagen.asf.ASF(path)
        rating = starsToWmaRating[stars]
        asf["WM/SharedUserRating"] = rating
        asf.save()
    elif ext(path) == "flac":
        asf = mutagen.flac.FLAC(path)
        asf["RATING"] = str(starsToFlacRating[stars])
        asf["RATING WMP"] = str(starsToFlacRatingWmp[stars])
        asf.save()


def wmaInfos(path):
    # print('.',)
    try:
        asf = mutagen.asf.ASF(path)
    except:
        print("impossible d'ouvrir asf de : " + path)
        return None
    infos = {"paths": [path]}
    for wmaTag, mp3Tag in wmaToMp3Tag.items():
        if wmaTag in asf and len(asf[wmaTag]) > 0:
            if wmaTag in ["Author", "Title"]:
                infos[mp3Tag] = str(asf[wmaTag][0])
            else:
                infos[mp3Tag] = asf[wmaTag][0].value
    if "WM/SharedUserRating" in asf and len(asf["WM/SharedUserRating"]) > 0:
        wmaRating = asf["WM/SharedUserRating"][0].value
        infos["stars"] = wmaRatingToStars[wmaRating]
    return infos


def tagInfos(path):
    if ext(path) == "mp3":
        return mp3Infos(path)
    elif ext(path) == "wma":
        return wmaInfos(path)
    else:
        return None


def smartInfos(path):

    infos = tagInfos(path)
    if infos is None:
        infos = dict()
    pInfos = pathInfos(path)

    for key, value in pInfos.items():
        if (key not in infos) or (key == "genre"):  # recupère le genre que j'ai impossé
            infos[key] = value

    if "genre" in infos and "maingenre" not in infos:
        genre = infos["genre"].upper()
        if genre in translateToMyGenre:
            genre = translateToMyGenre[genre]  # on ecrase pas le genre ?
        if genre in translateToMainGenre:
            infos["maingenre"] = translateToMainGenre[genre]
        else:
            infos["maingenre"] = "AUTRES STYLES"
    return infos


def artistTitle(infos):
    try:
        return " - ".join([infos["artist"], infos["title"]]).lower()
    except:
        print('impossible de generer "artist - Title" pour : ', infos["paths"][0])
        return name(
            infos["paths"][0]
        )  # permet d'eviter de planter quand je synchronise le disc ALL alors que y'a des mp3 correpondant à du youtube qui est sur le sansa
        # r#aise


def makeKey(infos):
    # if infos.has_key('albumartistsort') :
    #    key = ' - '.join([infos['albumartistsort'], infos['album'],infos['title']])
    # else :
    path = infos["paths"][0]
    namePath = name(path)
    try:
        if "album" in infos:
            key = " - ".join([infos["artist"], infos["album"], infos["title"]])
        else:
            key = " - ".join([infos["artist"], infos["title"]])

        if namePath[-1] == ")":
            if (namePath[-2] in "1234567890") and (
                (namePath[-3] == "(")
                or ((namePath[-3] in "1234567890") and (namePath[-4] == "("))
            ):
                key = key + " - " + infos["tracknumber"]
        return key.lower()
    except:
        # print("impossible de créer la clef pour ", infos['paths'][0], "utilise le nom du fichier : ",namePath.lower())
        # print(infos)
        return namePath.lower()


def makeTitleKey(infos):
    # if infos.has_key('albumartistsort') :
    #    key = ' - '.join([infos['albumartistsort'], infos['album'],infos['title']])
    # else :
    try:
        key = infos["title"]
        path = infos["paths"][0]
        namePath = name(path)
        if namePath[-1] == ")":
            if (namePath[-2] in "1234567890") and (
                (namePath[-3] == "(")
                or ((namePath[-3] in "1234567890") and (namePath[-4] == "("))
            ):
                key = key + " - " + infos["tracknumber"]
        return key.lower()
    except:
        print("impossible de créer la title clef pour ", infos["paths"][0])
        raise


def pathInfos(path):
    # splitFileName ne separe pas le nom du drive , car n'aura quasiment jamais a changer le nom du drive

    directory, name, ext = splitPath(path)
    directories = directory.split("/")

    infos = {"paths": [path], "pathSizes": [os.path.getsize(path)]}

    # recupère artiste - title à parir du nom du fichier
    nameSplit = name.split(" - ", 1)
    if len(nameSplit) == 2:
        [artist, title] = nameSplit
        infos["artist"] = artist
        infos["title"] = title
    else:
        # print("impossible de spliter :\n" + path)
        infos["title"] = name

    if len(directories) >= 1:
        # recupère artiste - album à parti du dossier parent

        if directories[-1].isupper() and directories[-1].find(" - ") == -1:
            # il semblerait que mp3 en vrac dans dossier d'un style ...
            if len(directories) >= 2 and "ALL" in directories:
                # recupère genre à parti du dossier parent
                if directories[-1].isupper():
                    genre = directories[-1].split(", ")[0]
                    if genre not in ["COMPILATION", "SOUNDTRACK", "EN VRAC", "ALL"]:
                        infos["genre"] = genre.title()

                    # recupère main genre à parti du dossier arrière-parent
                    if directories[-2].isupper():
                        maingenre = directories[-2]
                        if maingenre not in [
                            "COMPILATION",
                            "SOUNDTRACK",
                            "EN VRAC",
                            "ALL",
                        ]:
                            infos["maingenre"] = directories[-2]
        else:
            # recupère artiste - album à parti du dossier parent
            if directories[-1].find(" - ") != -1:
                albumArtist, album = directories[-1].split(" - ", 1)
                infos["album"] = album
                infos["albumartistsort"] = albumArtist
            else:
                album = directories[-1]
                infos["album"] = album

            if len(directories) >= 2 and "ALL" in directories:
                # recupère genre à parti du dossier arrière-parent
                if directories[-2].isupper():
                    genre = directories[-2].split(", ")[0]
                    if genre not in ["COMPILATION", "SOUNDTRACK", "EN VRAC", "ALL"]:
                        infos["genre"] = genre.title()

                    # recupère main genre à parti du dossier arrière-parent
                    if directories[-3].isupper():
                        maingenre = directories[-3]
                        if maingenre not in [
                            "COMPILATION",
                            "SOUNDTRACK",
                            "EN VRAC",
                            "ALL",
                        ]:
                            infos["maingenre"] = directories[-3]

    return infos


if __name__ == "__main__":
    try:
        # import ID3reader
        from SmartFramework.audioFiles import ID3
        from SmartFramework.files import cleanDropNames, changeExt
        from SmartFramework.serialize import serializePython

        cleanDropNames(sys.argv)
        paths = sys.argv[1:]  # #
        paths = [
            "A:/MUSIQUE/ALL/ELECTRO/ELECTRO/Daft Punk - Homework/Daft Punk - Da Funk.mp3"
        ]
        for path in paths:
            infos = smartInfos(path)
            print(infos)
        os.system("pause")

    except:
        import traceback

        # print("erreure avec le fichier : %s" % jsonPath)
        traceback.print_exc()
        os.system("pause")
