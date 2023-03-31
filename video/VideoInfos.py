import os
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata, config
from simplejson import loads
from parse import parse
import pickle
from SmartFramework.video.codecs import codec_extensions
from SmartFramework.files import name, ext, directory, addToName, joinPath

# permet d'eviter de tronquer la chaine de caractère contenant le json
config.MAX_STR_LENGTH = 0


def addTags(tags, path):
    if tags:
        if ext(path) == "avi":
            tagStrs = []
            for key, value in tags.items():
                tagStrs.append('%s="%s"' % (key, value.replace('"', '\\"')))
            tagStr = " ".join(tagStrs)
            ffmpegPath = joinPath(directory(__file__), "ffmpeg.exe")
            path_ = addToName(path, "_").replace("/", "\\")
            os.rename(path, path_)
            commande = '{ffmpegPath} -i "{path_}" -metadata {tagStr} -codec copy "{path.replace("/", "\\")}" && del "{path_}"'.format(
                **locals()
            )
            print(commande)
            os.popen(commande)
        else:
            print('unable to add tags to video without "avi" extension now')


class VideoInfos(object):
    def __init__(self, videoPath, forcePathParsing=False):
        self.__dict__["videoPath"] = videoPath
        self.__dict__["videoName"] = videoName = name(videoPath)
        # try to get info form Metadata
        video_ext = ext(videoPath)
        if ext in codec_extensions:
            file = open(videoPath, "rb")
            infos = pickle.load(file)
            file.close()
            self.__dict__.update(infos)
            return None

        if video_ext == "avi":
            parser = createParser(videoPath)
            self._metadata = extractMetadata(parser)
            if self._metadata is not None:
                commentItem = self._metadata.getItem("comment", 1)
                if (commentItem is not None) and (not forcePathParsing):
                    jsonStr = commentItem.value
                    jsonDict = loads(jsonStr)
                    for key, value in jsonDict.items():
                        # on a mal serilizé des int en les mettant sous forme de string, coo
                        if isinstance(value, str) and value.lstrip("-").isnumeric():
                            value = int(value)
                        self.__dict__[key] = value
                    for data in self._metadata:
                        if data.values:
                            key = data.key
                            if key != "comment":
                                for value in data.values:
                                    self.__dict__[key] = value.value
                    if jsonDict:
                        return None
        # try to get info form file name
        if videoName is not None:
            result = parse(
                "{firstName}_{lastName}_{whiteMarkersStr}_d={distance}_x={x}_y={y}_{expressions}",
                videoName,
            )
            if result is None:
                result = parse(
                    "{firstName}_{lastName}_d={distance}_x={x}_y={y}_{expressions}",
                    videoName,
                )
            if result is None:
                result = parse("{firstName}_{lastName}_IR_400_{expressions}", videoName)
            if result is not None:
                infos = result.named
                for key in ["x", "y", "distance"]:
                    if key in infos:
                        if infos[key].lstrip("-").isnumeric():
                            infos[key] = int(infos[key])
                    else:
                        infos[key] = "var"
                infos["whiteMarkers"] = "whiteMarkersStr" in infos
                self.__dict__.update(infos)

    def getDefaultPositionsFileName(self):
        try:
            return "{firstName}_{lastName}_d={distance}_x={x}_y={y}_defaultPositions.json".format(
                **self.__dict__
            )
        except:
            return None

    defaultPositionsFileName = property(getDefaultPositionsFileName)
