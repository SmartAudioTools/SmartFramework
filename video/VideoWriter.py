# -*- coding: utf-8 -*-
import cv2
import numpy

# /!\ keep this line ! useful to add ZSTD and PICK codecs:
from SmartFramework.video import codecs
from SmartFramework.video.VideoInfos import addTags


class VideoWriter:
    """API slightly different from cv2.VideoWriter :
    - no need to specify the size and isColor to __init__ (it will be taken from the first image)
    - you can add tags

    - check for memory space before writing if availableMemory argument given to write method.
    - "path" argument instead of "filename"
    - "codec" string argument instead of "fourcc"int

    """

    def __init__(self, path, codec, fps, tags):
        self.path = path
        self.codec = codec
        self.fps = fps
        self.tags = tags
        self._first_image = True

    # def setTags(self,tags):
    #    """allow to set tags after writing frames"""
    #    self.tags = tags

    def write(self, obj, availableMemory=None):
        if self._first_image:
            self._first_image = False
            shape = obj.shape
            size = (shape[1], shape[0])
            # B&N NE MARCE PAS avec LAGS, enregistre fichier vide :
            isColor = bool(len(shape) > 2 or self.codec == "LAGS")
            self.onDiskSize = numpy.prod(shape)
            self.videoWriter = cv2.VideoWriter()
            retval = self.videoWriter.open(
                self.path, fourcc(self.codec), self.fps, size, isColor
            )
            self.videoWriter.tags = self.tags
            if not retval:
                if self.codec == "LAGS" and cv2.__version__ > "3.4.3":
                    raise Exception(
                        "Open CV ne supporte plus le codec LAGS en ecriture après la version 3.4.3"
                    )
                raise Exception(
                    "Impossible d'ouvrire le fichier video %s en ecriture , verifiez que le codec est installe"
                    % self.path
                )
        if (availableMemory is not None) and availableMemory < self.onDiskSize:
            return 0
        else:
            self.videoWriter.write(obj)
            return self.onDiskSize

    def __del__(self):
        if self.videoWriter._use_cv2_VideoWriter and self.tags:
            del self.videoWriter
            addTags(tags=self.tags, path=self.path)
        else:
            del self.videoWriter


def fourcc(codec):
    if codec == "Menu":
        return -1
    else:
        return cv2.VideoWriter_fourcc(*str(codec))
