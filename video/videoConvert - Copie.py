import cv2
import os
import numpy as np
from scipy import ndimage
from SmartFramework.files import splitPath, joinPath, addToName
from SmartFramework.files import dragAndDrop

videoExtensions = ("avi", "mp4", "zstd")


def videoConvert(path, start=0, stop=None, step=1, outExt="zstd", codec="ZSTD"):

    path = path.replace("\\", "/")
    print("converting ", path)
    directory, name, ext = splitPath(path)

    videoCapture = cv2.VideoCapture()
    retval = videoCapture.open(path)
    if not retval:
        raise Exception(
            "Impossible d'ouvrire le fichier , verifiez que le codec est installe"
        )

    totalImages = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
    totalDigits = len(str(totalImages - 1))

    videoCapture.set(cv2.CAP_PROP_POS_FRAMES, start)
    retval, image = videoCapture.read()
    if not retval:
        raise Exception(
            "Impossible de decoder le fichier , verifiez que le codec est installe"
        )

    shape = image.shape

    size = (newShape[1], newShape[0])
    # size = (newShape[0],newShape[1])
    if outExt in videoExtensions:
        videoWriter = cv2.VideoWriter()
        outPath = joinPath(directory, name, outExt)
        if outPath == path:
            outPath = addToName(path, "_")
        if len(shape) > 2 or (
            codec not in ["DIB "]
        ):  # B&N NE MARCE PAS avec LAGS !!!! enregistre fichier vide !!!
            videoWriteInColor = True
        else:
            videoWriteInColor = False
        fps = videoCapture.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*str(codec))
        print(codec, fourcc)
        succes = videoWriter.open(outPath, fourcc, fps, size, videoWriteInColor)
        print(succes)
    else:
        if not os.path.exists(outDirectory):
            os.mkdir(outDirectory)

    i = start
    while retval and (stop is None or i <= stop):
        # print(i)
        if not color:
            image = image[:, :, 1]
        if cropZone is not None:
            xStart, yStart, width, height = cropZone
            xStop, yStop = xStart + width, yStart + height
            image = image[yStart:yStop, xStart:xStop]
        if rotation:
            image = np.rot90(image, rotation // 90)

        # traitements en float  -----------------
        imageFloat = None
        if passeHaut:
            if imageFloat is None:
                imageFloat = image.astype(np.float)
            blurred = ndimage.gaussian_filter(imageFloat, sigma=5.0)
            imageFloat = (imageFloat - blurred) + 125.0
        if contrast != 1.0:
            if imageFloat is None:
                imageFloat = image.astype(np.float)
            imageFloat = a * imageFloat + b
        if imageFloat is not None:
            image = imageFloat
        # ------------------------------------------

        if resize != 1.0:
            image = cv2.resize(image, size)

        if (paddingWidth is not None) or (paddingHeight is not None):
            paddedImage = np.zeros((paddingHeight, paddingWidth), np.uint8)
            paddedImage[: shape[0], : shape[1]] = image
            image = paddedImage

        if outExt in videoExtensions:
            # print(image.shape)
            videoWriter.write(image.astype(np.uint8))
        else:
            toFormat = "{}.{:0>%d}" % totalDigits
            outFileName = joinPath(outDirectory, toFormat.format(name, i), outExt)
            if outExt == "jpg":
                cv2.imwrite(
                    outFileName, np.copy(image), (cv2.IMWRITE_JPEG_QUALITY, jpegQuality)
                )  # [cv.CV_IMWRITE_PNG_COMPRESSION,9] => donne images plus grosses !?
            else:
                cv2.imwrite(outFileName, np.copy(image))

        i += step
        if step != 1:
            videoCapture.set(cv2.CAP_PROP_POS_FRAMES, i)
        retval, image = videoCapture.read()
    if videoWriter is not None:
        del videoWriter


if __name__ == "__main__":
    import sys

    sys.argv = ["", "D:/Baptiste.avi"]
    dragAndDrop(callback=videoConvert, extension="avi", recursive=True)
