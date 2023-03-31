import cv2
import os
import numpy as np
from scipy import ndimage
from SmartFramework.files import splitPath, joinPath, addToName
from SmartFramework.files import dragAndDrop
from SmartFramework.video import codecs

videoExtensions = ("avi", "mp4", "zstd", "pkl", "pickle")


def videoConvert(
    path,
    start=0,
    stop=None,
    step=1,
    contrast=1.0,
    center=0.5,
    rotation=0,
    outExt="zstd",  # "avi", #'png'#
    jpegQuality=95,
    # color=True,
    passeHaut=False,
    resize=1.0,
    codec="ZSTD",  # codec de sortie
    cropZone=None,
    outDirectory=None,
    onlyNotAlreadyConverted=True,
    paddingWidth=None,
    paddingHeight=None,
):

    path = path.replace("\\", "/")
    print("converting ", path)
    directory, name, ext = splitPath(path)

    if outExt in videoExtensions:
        outPath = joinPath(directory, name, outExt)
        if onlyNotAlreadyConverted and os.path.exists(outPath):
            return
    else:
        if outDirectory is None:
            outDirectory = joinPath(directory, name)
        if onlyNotAlreadyConverted and os.path.exists(outDirectory):
            return

    # contrastAndCenters   =  [[contrast,contrastCenter]] #     [[3.,0.6],[2.,0.5],[1.5,0.5]]    # 0.-infinity

    # cropZone = [242,62,240,320] #  []  left_x, up_y, width, height
    if cropZone is not None:
        cropZone[2] = int(round(cropZone[2] / 8)) * 8
        cropZone[3] = int(round(cropZone[3] / 8)) * 8

    # for contrast , center in  contrastAndCenters:
    videoWriter = None
    # name = name + '_('
    if cropZone is not None:
        name = "{}_cropped({}x{})".format(name, cropZone[2], cropZone[3])
    if contrast != 1.0:
        name = "{}_contrast_{}_center_{}".format(name, contrast, center)
    if step != 1:
        name = "{}_step_{}".format(name, step)

    # name = '{}_{})'.format(name,outExt)

    # fatherDirectory = joinPath(directory,name)

    # if not os.path.exists(fatherDirectory) :
    #    os.mkdir(fatherDirectory)

    videoCapture = cv2.VideoCapture()
    retval = videoCapture.open(path)
    if not retval:
        raise Exception(
            "Impossible d'ouvrire le fichier , verifiez que le codec est installe"
        )

    totalImages = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
    # print(totalImages)
    # print(str(totalImages-1))
    totalDigits = len(str(totalImages - 1))
    # print(totalDigits)

    videoCapture.set(cv2.CAP_PROP_POS_FRAMES, start)
    retval, image = videoCapture.read()
    color = np.sum(np.diff(image, axis=2)) > 0

    if not retval:
        raise Exception(
            "Impossible de decoder le fichier , verifiez que le codec est installe"
        )

    if image.dtype == np.uint8:  # 0-256
        a = float(contrast)
        b = center * (1.0 - float(contrast)) * 256.0
    else:
        raise Exception("format de matrice numpy different de np.uint8")

    shape = image.shape

    if cropZone is not None:
        xStart, yStart, width, height = cropZone
        xStop, yStop = xStart + width, yStart + height
        xStart = max(xStart, 0)
        yStart = max(yStart, 0)
        xStop = min(xStop, shape[1])
        yStop = min(yStop, shape[0])  # a verifier
        shape = (yStop - yStart, xStop - xStart)
    if resize != 1.0:
        newShape = [int(image.shape[0] * resize), int(image.shape[1] * resize)]
        name = "{}_resized({}x{})".format(name, newShape[1], newShape[0])
    else:
        newShape = list(shape)

    if (paddingWidth is not None) or (paddingHeight is not None):
        if paddingWidth is not None:
            newShape[1] = paddingWidth
        if paddingHeight is not None:
            newShape[0] = paddingHeight
        name = "{}_padded({}x{})".format(name, newShape[1], newShape[0])

    size = (newShape[1], newShape[0])
    # size = (newShape[0],newShape[1])
    if outExt in videoExtensions:
        videoWriter = cv2.VideoWriter()
        outPath = joinPath(directory, name, outExt)
        if outPath == path:
            outPath = addToName(path, "_")
        fps = videoCapture.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*str(codec))
        retval = videoWriter.open(outPath, fourcc, fps, size, color)
        if not retval:
            if codec == "LAGS" and cv2.__version__ > "3.4.3.18":
                raise Exception(
                    "Open CV ne supporte plus le codec LAGS après la version 3.4.3.18"
                )
            raise Exception(
                "Impossible d'ouvrire le fichier video %s en ecriture , verifiez que le codec est installe"
                % outPath
            )
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

    # sys.argv = ["", "D:/Baptiste.avi"]
    sys.argv = [
        "",
        "D:/Documents/Bureau/Nouveau dossier/Baptiste_DeLaGorce_wm_d=35_x=0_y=10_Nose.avi",
    ]
    dragAndDrop(callback=videoConvert, extension="avi", recursive=True)
