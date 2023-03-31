import numpy as numpy
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.image.numpy2qimage import numpy2qimage
from SmartFramework.serialize import serializejson


gray_table = [(255 << 24) + (g << 16) + (g << 8) + g for g in range(256)]
green_table = [(255 << 24) + (g << 8) for g in range(256)]


def asNumpy(QPointF):
    return numpy.array((QPointF.x(), QPointF.y()), dtype=float)


class ImageShowAlphaUI(QtWidgets.QWidget):
    # class ImageShowUI(QtWidgets.QOpenGLWidget):
    # constructor

    def __init__(
        self,
        parent=None,
        smooth=True,
        autoRescale=True,
        mirror=False,
        noSystemBackground=True,
        serializeImage=False,
        **kwargs
    ):
        # QtWidgets.QOpenGLWidget.__init__(self, parent, **kwargs)
        QtWidgets.QWidget.__init__(self, parent, **kwargs)

        # save arguments
        self.smooth = smooth
        self.autoRescale = autoRescale
        self.mirror = mirror
        self._serializeImage = serializeImage

        # image
        self.image = None
        self._QImage = None
        self.image2 = None
        self._QImage2 = None

        # zoom et translation
        self._wheelZoomFactor = 0.1
        self._pointMoveFactor = 0.25
        self.translation = numpy.array([0.0, 0.0])
        self.scale = 1.0
        self.autoScale = 1.0
        self.autoScaleTranslation = numpy.array([0.0, 0.0])
        self._transform = QtGui.QTransform()
        self.updateTransform()
        self.noSystemBackground = noSystemBackground
        self.image2Alpha = 127
        self.image_table = gray_table

    # Methodes -----------------------

    def getNoSystemBackground(self):
        return self.testAttribute(QtCore.Qt.WA_NoSystemBackground)

    def setNoSystemBackground(self, value):
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, value)

    noSystemBackground = QtCore.Property(
        bool, getNoSystemBackground, setNoSystemBackground
    )

    def positionFromQPixel(self, pixel):
        # QPointF = self._transform.inverted()[0].map(pixel)
        # return numpy.array((QPointF.x(),QPointF.y()),dtype = numpy.float)
        pixelNp = numpy.array((pixel.x(), pixel.y()), dtype=float)
        return (pixelNp - (self.translation + self.autoScaleTranslation)) * (
            1.0 / (self.scale * self.autoScale)
        )

    def inZoom(self, scale, pixel):
        # print(scale)
        position = self.positionFromQPixel(pixel)
        self.translation = (
            asNumpy(pixel) - scale * self.autoScale * position
        ) - self.autoScaleTranslation
        self.scale = scale
        self.updateTransform()
        self.repaint()

    def updateTransform(self):
        self._transform.reset()
        # doit être avant le scale , sinon la translation se fait dans le repère agrandit...
        scale = self.scale * self.autoScale
        translation = (self.translation + self.autoScaleTranslation).astype(int)
        if self.image is not None:
            h, w = self.image.shape[:2]
            translation = translation.clip(
                numpy.array([self.width(), self.height()])
                - scale * numpy.array([w, h]),
                0,
            )
        self._transform.translate(*translation)
        self._transform.scale(scale, scale)

    # Events ------------------------------

    def wheelEvent(self, event):
        try:
            delta = self._wheelZoomFactor * event.angleDelta().y() / 120.0
        except:
            delta = self._wheelZoomFactor * event.delta() / 120.0  # PyQt4
        newScale = self.scale + delta
        if newScale < 1:
            self.inZoom(1, QtCore.QPointF(event.pos()))
            self.translation = self.translation * newScale
        else:
            self.inZoom(newScale, QtCore.QPointF(event.pos()))
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
            # self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            try:
                pixel = event.localPos()
            except:
                pixel = event.posF()  # pyqt4
            self._oldMousePixel = asNumpy(pixel)
            self.setCursor(QtCore.Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            try:
                pixel = event.localPos()
            except:
                pixel = event.posF()  # pyqt4
            newMousePixel = asNumpy(pixel)
            deltaPixel = newMousePixel - self._oldMousePixel
            self._oldMousePixel = newMousePixel
            self.translation = self.translation + deltaPixel
            self.updateTransform()
            self.repaint()

    def paintEvent(self, event, painter=None):
        if self.image is not None or self.image2 is not None:

            self.updateAutoscale()
            if painter is None:
                painter = QtGui.QPainter(self)
            painter.setWorldTransform(self._transform)
            if self.smooth:
                painter.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
            if self.image is not None:
                if self._QImage is None:
                    if self.mirror:
                        image = numpy.fliplr(self.image)
                    else:
                        image = self.image
                    if self.image2 is not None and self.image2Alpha:
                        self._QImage = numpy2qimage(
                            image, QtGui.QImage.Format_Indexed8, color_table=green_table
                        )
                    else:
                        self._QImage = numpy2qimage(image, QtGui.QImage.Format_RGB32)

                painter.drawImage(0, 0, self._QImage)

            if self.image2 is not None and self.image2Alpha:
                if self._QImage2 is None:
                    if self.mirror:
                        image2 = numpy.fliplr(self.image2)
                    else:
                        image2 = self.image2
                    self._QImage2 = numpy2qimage(
                        image2,
                        QtGui.QImage.Format_Indexed8,
                        color_table=self.image2_table,
                    )
                painter.drawImage(0, 0, self._QImage2)

        # return painter

    # slots ------------------------
    @QtCore.Slot(object)
    def inImage(self, image):
        if isinstance(image, QtGui.QImage):
            self.image = image
            self._QImage = image
        else:
            self.image = image
            self._QImage = None
        self.update()

    @QtCore.Slot(object)
    def inImage2(self, image):
        if isinstance(image, QtGui.QImage):
            self.image2 = image
            self._QImage2 = image
        else:
            self.image2 = image
            self._QImage2 = None
        self.update()

    @QtCore.Slot(int)
    def setImage2Alpha(self, alpha):
        self.image2Alpha = alpha
        self._QImage2 = None
        # self.image2_table = [(alpha << 24) + (g << 16) for g in range(256)]
        self.image2_table = [(alpha << 24) + (g << 16) + g for g in range(256)]
        self.update()

    def updateAutoscale(self):
        if self.autoRescale and self.image is not None:
            if isinstance(self.image, QtGui.QImage):
                h = self.image.height()
                w = self.image.width()
            else:
                h, w = self.image.shape[:2]

            scaleX = float(self.height()) / h
            scaleY = float(self.width()) / w
            autoScale = max(scaleX, scaleY)
            if self.autoScale != autoScale:
                self.autoScale = autoScale
                # self.scale = 1.
                if scaleX < scaleY:
                    self.autoScaleTranslation[0] = 0
                    self.autoScaleTranslation[1] = (
                        -((h * autoScale) - self.height()) / 2
                    )
                else:
                    self.autoScaleTranslation[0] = -((w * autoScale) - self.width()) / 2
                    self.autoScaleTranslation[1] = 0
                # print("new autoScale : ", autoScale)
                # print("new autoScaleTranslation : ", self.autoScaleTranslation)
                self.updateTransform()

    @QtCore.Slot(float)
    def setScale(self, scale):
        self.__dict__["scale"] = scale
        self.updateTransform()
        self.update()

    @QtCore.Slot(object)
    def setTranslation(self, translation):
        self.__dict__["translation"] = translation
        self.updateTransform()
        self.update()

    @QtCore.Slot(bool)
    def setMirror(self, mirror):
        self.__dict__["mirror"] = mirror
        self._QImage = None
        self._QImage = None
        self.update()

    def getMirror(self):
        return self.__dict__["mirror"]

    mirror = QtCore.Property(bool, getMirror, setMirror)

    def resizeToImage(self):
        self.resize(self.image.shape[1], self.image.shape[0])

    def __getstate__(self):
        if self._serializeImage:
            return serializejson.getstate(self)
        else:
            return serializejson.getstate(self, remove=["image"])


if __name__ == "__main__":
    import sys
    import cv2
    import numpy
    import math

    app = QtWidgets.QApplication(sys.argv)
    image = cv2.imread("SAT.png", cv2.IMREAD_UNCHANGED)
    widget = ImageShowUI(noSystemBackground=False)
    widget.inImage(image)
    widget.show()
    app.exec_()
