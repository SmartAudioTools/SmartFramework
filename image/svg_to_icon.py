# -*- coding: utf-8 -*-
"""
Created on Fri May 20 00:23:57 2022

@author: Baptiste
"""

from qtpy import QtGui, QtSvg
from SmartFramework.files import splitPath, joinPath
import numpy
import cv2
import qimage2ndarray


def convertSvgToPng(
    svgFilepath, pngFilepath, width, backgroundColor=(255, 255, 255, 255), clear=True
):
    renderer = QtSvg.QSvgRenderer(svgFilepath)
    height = renderer.defaultSize().height() * width / renderer.defaultSize().width()

    if clear:
        channels = []
        for channel_number, translate in enumerate((-1 / 3, 0, 1 / 3)):
            qimage = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
            qimage.fill(QtGui.QColor(*backgroundColor))
            painter = QtGui.QPainter(qimage)
            transform = QtGui.QTransform()
            transform.translate(translate, 0)
            painter.setWorldTransform(transform)
            renderer.render(painter)
            channel = qimage2ndarray.byte_view(qimage)[:, :, channel_number]
            channels.append(channel)
        image = numpy.stack(channels, axis=2)
        cv2.imwrite(pngFilepath, image)
    else:
        qimage = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
        qimage.fill(QtGui.QColor(*backgroundColor))
        painter = QtGui.QPainter(qimage)
        renderer.render(painter)
        qimage.save(pngFilepath)
    painter.end()


path = "SAT.svg"
clear = False
width = 256
for clear in [False, True]:
    clear_str = "clear" if clear else "clasic"
    folder, name, ext = splitPath(path)
    out_path = joinPath(folder, f"{name}_{width}_{clear_str}", "png")
    convertSvgToPng(path, out_path, width, clear=clear)
