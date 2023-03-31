# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 22:13:02 2021

@author: Baptiste
"""

import numpy
import pickle
import blosc
import struct
from SmartFramework.optimize.numpa import cumsum, add
from SmartFramework.files import ext
import cv2

try:
    from cv2 import cv2_VideoCapture
except:
    from cv2 import VideoCapture as cv2_VideoCapture
from SmartFramework.video.VideoWriter import codec_extensions


# compile or load cashed numpa function
a = numpy.empty((640, 480), dtype="uint8")
b = numpy.empty((640, 480), dtype="uint8")
out = cumsum(a, 1)
cumsum(a, 1, out=out)  # plante
out = add(a, b)
add(a, b, out=out)


class VideoCapture:
    def __init__(self, path=None, *args, **kargs):
        self.flag = "coucou"
        if path is not None:
            self.open(path, *args, **kargs)

    def open(self, path, *args, **kargs):
        if ext(path) not in codec_extensions:
            self._use_cv2_VideoCapture = True
            value = self._cv2_VideoCapture = cv2_VideoCapture()
            return value.open(path, *args, **kargs)

        self._use_cv2_VideoCapture = False
        # if not os.path.exists(path):
        #    return False
        file = self._file = open(path, "rb")

        # recupère la table d'offsets à la fin du fichier
        # (faudrait pouvoir s'en passer si le fichier n'a pas été correctement fermé lors d'un plantage)
        file.seek(-8, 2)
        len_pickled_offsets = struct.unpack("Q", file.read(8))[0]
        file.seek(-(len_pickled_offsets + 8), 2)
        self._end_offset = file.tell()
        self._offsets = pickle.load(file)

        # recupère les infos au début du fichier
        file.seek(0)
        infos = pickle.load(file)
        self.__dict__.update(infos)
        self._next_index = 0
        self.step = 1
        self._last_key_image_and_index = (None, None)
        self._opened = True
        return True

    # @profile
    def read(self, i=None):
        if self._use_cv2_VideoCapture:
            if i is not None:
                self._cv2_VideoCapture.set(cv2.CAP_PROP_POS_FRAMES, i)
            return self._cv2_VideoCapture.read()
        if not self._opened:
            return (False, None)
        if i is None:
            i = self._next_index
        file = self._file
        if i < len(self._offsets):
            offset, key_index = self._offsets[i]
        else:
            return False, None
        if offset != file.tell():
            file.seek(offset)
        loaded = pickle.load(file)  # 0.084msec 14.8%
        if self.codec == "PICK":
            image = loaded
        elif self.codec == "ZSTD":
            shape, dtype, compressed = loaded
            blosc.set_nthreads(8)

            decoded_bytearray = blosc.decompress(compressed, as_bytearray=True)  # 46%
            image = numpy.ndarray(shape, dtype, decoded_bytearray)
            if i == key_index:
                # numpy.cumsum(image, axis=self.axis, out=image)  # 0.672
                last_key_image, last_key_index = self._last_key_image_and_index
                if last_key_index == i:
                    # a priori lecture à l'envers et on a déjà lu la key frame
                    image = last_key_image
                else:
                    cumsum(image, self.axis, out=image)  # 0.237 6.2%
                    self._last_key_image_and_index = (image, i)
            else:
                last_key_image, last_key_index = self._last_key_image_and_index
                if key_index != last_key_index:
                    retval, last_key_image = self.read(key_index)
                    if not retval:
                        raise Exception("impossible de lire la key image")
                # image += last_key_image  # 0.314 msec
                add(image, last_key_image, out=image)  # 0.162msec 22.8%
        else:
            raise Exception("Custom codec reader not yet implemented")
        self._next_index = i + self.step
        return True, image

    def set(self, parameter, value):
        if self._use_cv2_VideoCapture:
            return self._cv2_VideoCapture.set(parameter, value)
        elif parameter == cv2.CAP_PROP_POS_FRAMES:
            self._next_index = value
            return True
        else:
            raise Exception("VideoCapture.set parameter unknow")

    def get(self, parameter):
        if self._use_cv2_VideoCapture:
            return self._cv2_VideoCapture.get(parameter)
        elif parameter == cv2.CAP_PROP_FPS:
            return self.fps
        elif parameter == cv2.CAP_PROP_FRAME_COUNT:
            return len(self._offsets)
        else:
            raise Exception("VideoCapture.get parameter unknow")

    def release(self):
        if self._use_cv2_VideoCapture:
            return self._cv2_VideoCapture.release()

    def __del__(self):

        if self._use_cv2_VideoCapture:
            del self._cv2_VideoCapture
        else:
            self._file.close()

    def grab(self):
        if self._use_cv2_VideoCapture:
            return self._cv2_VideoCapture.grab()
        else:
            self._next_index += self.step
