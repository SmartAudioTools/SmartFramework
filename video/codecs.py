# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 14:51:04 2021

@author: Baptiste
"""
import pickle
import blosc
import numpy
import struct
import cv2
from SmartFramework.tools.dictionaries import filtered
from SmartFramework.optimize.numpa import diff, subtract, cumsum, add
from SmartFramework.video.key_frame_detector import key_frame_detector
from SmartFramework.files import ext


codec_names = ("ZSTD", "PICK")  # , "JSON"]
codec_extensions = ["pickle", "pkl", "zstd"]

# -------------------------------
cv2_VideoCapture = cv2.cv2_VideoCapture = cv2.VideoCapture
cv2_VideoWriter = cv2.cv2_VideoWriter = cv2.VideoWriter

# compile or load cashed numpa function
a = numpy.empty((640, 480), dtype="uint8")
b = numpy.empty((640, 480), dtype="uint8")
# for writer
out = diff(a, 1)
diff(a, 1, out=out)
out = subtract(a, b)
subtract(a, b, out=out)
key_frame_detector(a, b, 8)
# for reader
out = cumsum(a, 1)
cumsum(a, 1, out=out)  # plante
out = add(a, b)
add(a, b, out=out)


class VideoWriter:
    """
    cv2.videoWriter monkey patching with ZSTD and PICK new codecs and exactly the same API
    """

    def __init__(
        self, filename=None, fourcc=None, fps=None, frameSize=None, isColor=True
    ):
        self._file = None
        if filename is not None:
            self.open(filename, fourcc, fps, frameSize, isColor)

    def open(self, filename, fourcc, fps, frameSize, isColor=True):

        # opencv codecs ----------------------

        if not fourcc in codec_fourccs:
            self._use_cv2_VideoWriter = True
            if fourcc == cv2.VideoWriter_fourcc(*"LAGS"):
                isColor = True
            self._cv2_VideoWriter = cv2_VideoWriter(
                filename, fourcc, fps, frameSize, isColor=isColor
            )
            return self._cv2_VideoWriter

        # custom codecs ---------------------

        self._use_cv2_VideoWriter = False
        self.codec = codec_name_from_fourcc[fourcc]
        self.fps = fps
        self.diff_axis = 1  # axe pour diff et cumsum
        self._image_index = -1
        self._offsets = []
        self.tags = None
        try:
            file = open(filename, "wb")
        except:
            self._file = None
            return False
        self._file = file
        return True

        # @profile

    def write(self, image):
        # opencv codecs ----------------------
        if self._use_cv2_VideoWriter:
            return self._cv2_VideoWriter.write(image)

        # custom codecs ---------------------
        self._image_index += 1
        first_image = self._image_index == 0
        if first_image:
            self._last_key_image = numpy.zeros(image.shape, dtype=image.dtype)
            self._diff_image = numpy.empty(image.shape, dtype=image.dtype)
            # enregistre les infos !
            infos = {"codec": self.codec, "fps": self.fps, "diff_axis": self.diff_axis}
            if self.tags is not None:  # not in cv2.VideoWriter API
                infos.update(self.tags)
            pickle.dump(infos, self._file)

        if self.codec == "ZSTD":
            blosc.set_nthreads(8)
            # key_frame_detector :
            # step 16 -> 0.020 2.8%
            # step 8 -> 0.020 2.9%
            # step 4 -> 0.031 4.3%
            if first_image or key_frame_detector(image, self._last_key_image, 8):
                # diff_image = diff(image, 1, self._diff_image)  # 0.126 et empeche changment dynamic de resolution / color
                diff_image = diff(image, 1)  # 0.075 1%
                self._last_key_image = image
                self._key_index = self._image_index
            else:
                diff_image = subtract(image, self._last_key_image)  # 0.143 17%
                # diff_image = image - self._last_key_image  # 0.342
            self._last_image = image
            compressed = blosc.compress(  # 0.22 59%
                diff_image,
                diff_image.itemsize,
                cname=self.codec.lower(),
                clevel=1,
            )
            offset = self._file.tell()
            self._offsets.append((offset, self._key_index))
            # self._file.write(compressed)  # 0.067  7.5%
            # pickle :
            # rajoute 7 octets par rapport à des bytes pure et pas plus lent
            # 0.097 13%, plus long (recopie ? ) mais plus sur si plantage avant fermeture du fichier
            pickle.dump((image.shape, image.dtype, compressed), self._file)

        elif self.codec == "PICK":
            offset = self._file.tell()
            self._offsets.append((offset, offset))
            pickle.dump(image, self._file)
        else:
            raise Exception("Custom codec writer not yet implemented")

    def set(self, parameter, value):
        if self._use_cv2_VideoCapture:
            return self._cv2_VideoCapture.set(parameter, value)
        else:
            raise Exception("VideoCapture.set parameter unknow")

    def get(self, parameter):
        if self._use_cv2_VideoCapture:
            return self._cv2_VideoCapture.get(parameter)
        else:
            raise Exception("VideoCapture.get parameter unknow")

    def __del__(self):
        if self._use_cv2_VideoWriter:
            del self._cv2_VideoWriter
        else:
            self.release()

    def release(self):
        if self._use_cv2_VideoWriter:
            self._cv2_VideoWriter.release()
        else:
            # print("del videoWriter")
            # infos = pickle.dumps(filtered(self.__dict__))
            offsets = pickle.dumps(self._offsets)
            self._file.write(offsets)
            self._file.write(struct.pack("Q", len(offsets)))
            self._file.close()


cv2.VideoWriter = VideoWriter  # va remplacer dans tous les scripts !


class VideoCapture:
    """
    cv2.VideoCapture monkey patching with new codecs
    """

    def __init__(self, path=None, *args, **kargs):
        self._opened = False
        if path is not None:
            self.open(path, *args, **kargs)

    def open(self, path, *args, **kargs):

        # webcam or opencv codecs ----------------------

        if isinstance(path, int) or ext(path) not in codec_extensions:
            self._use_cv2_VideoCapture = True
            value = self._cv2_VideoCapture = cv2_VideoCapture()
            return value.open(path, *args, **kargs)

        self._use_cv2_VideoCapture = False
        file = self._file = open(path, "rb")

        # custom codecs ---------------------

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
        self.fps = infos["fps"]
        self.codec = infos["codec"]
        self.diff_axis = infos["diff_axis"]
        self._next_index = 0
        self.step = 1
        self._last_key_image_and_index = (None, None)
        self._opened = True
        return True

    def isOpened(self):
        if self._use_cv2_VideoCapture:
            return self._cv2_VideoCapture.isOpened()
        else:
            return (self._opened) and (self._next_index < len(self._offsets))

    # @profile

    def read(self, i=None):

        # webcam or opencv codecs ----------------------

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
                # numpy.cumsum(image, diff_axis=self.diff_axis, out=image)  # 0.672
                last_key_image, last_key_index = self._last_key_image_and_index
                if last_key_index == i:
                    # a priori lecture à l'envers et on a déjà lu la key frame
                    image = last_key_image
                else:
                    cumsum(image, self.diff_axis, out=image)  # 0.237 6.2%
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


cv2.VideoCapture = VideoCapture  # va remplacer dans tous les scripts !
codec_fourccs = [cv2.VideoWriter_fourcc(*elt) for elt in codec_names]
codec_name_from_fourcc = dict(zip(codec_fourccs, codec_names))
codec_fourcc_or_names = set(codec_names).union((codec_fourccs))
