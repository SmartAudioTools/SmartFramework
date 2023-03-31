import cv2  # pause probleme pour debugage
import numpy
import os


def contrastLuminosity(image, contrast, luminosity, center=0.5):
    imageFloat = image.astype(numpy.float, copy=False)
    a = float(contrast)
    b = (center * (1.0 - float(contrast)) + luminosity) * 256.0
    return a * imageFloat + b


def isascii(s):
    return len(s) == len(s.encode())


def imwrite(filename, img, *args, **argsDict):
    """Corrige bug d'open cv qui fait de la merde avec les path contenant unicode"""
    if isascii(filename):
        cv2.imwrite(filename, img, *args, **argsDict)
    else:
        cv2.imencode(os.path.splitext(filename)[1], img, *args, **argsDict)[1].tofile(
            filename
        )


def imread(filename, *flags):
    if isascii(filename):
        return cv2.imread(filename, *flags)
    else:
        stream = open(filename, "rb")
        bytesArray = bytearray(stream.read())
        stream.close()
        numpyarray = numpy.asarray(bytesArray, dtype=numpy.uint8)
        return cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED, *flags)
