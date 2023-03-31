import numpy as numpy
from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.tools.objects import add_Args
from SmartFramework.tools.dictionaries import remove
from SmartFramework.image.numpy2qimage import numpy2qimage, QImage
from SmartFramework.ui.Trackpad import Trackpad


def asNumpy(QPointF):
    return numpy.array((QPointF.x(), QPointF.y()), dtype=numpy.float)


class ImageShowWithCursorUI(QtWidgets.QWidget, Trackpad):

    outX = QtCore.Signal((int,), (float,))

    # constructor

    def __init__(
        self,
        parent=None,
        serializeImage=True,
        serialize=True,
        smooth=True,
        autoRescale=True,
        **kwargs
    ):
        add_Args(locals())
        self._all = False
        QtWidgets.QWidget.__init__(self, parent, **kwargs)
        Trackpad.__init__(self)
        self.smooth = smooth

        # zoom et translation
        self._wheelZoomFactor = 0.1
        self._pointMoveFactor = 0.25
        self.autoRescale = autoRescale
        self.translation = numpy.array([0.0, 0.0])
        self.scale = 1.0
        self.autoScale = 1.0
        self.autoScaleTranslation = numpy.array([0.0, 0.0])
        self._transform = QtGui.QTransform()
        self.updateTransform()
        self.updateCurrentImage = True
        # if not self.updateCurrentImage:
        # suprime l'initialisation du baground car de tout facon affiche une image
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.image = None
        self._QImage = None
        self.xmin = 0.0
        self.xmax = 1.0
        self.useIntX = False
        self._xCursor = None
        self._xCursorPen = QtGui.QPen()
        self._xCursorPen.setCosmetic(True)
        self._xCursorPen.setColor(QtGui.QColor(255, 0, 0, 255))
        self._xCursorPen.setWidthF(2.0)
        self._movingImage = False
        self._movingCursor = False

    # Methodes -----------------------

    def QpixelToPosition(self, pixel):
        # QPointF = self._transform.inverted()[0].map(pixel)
        # return numpy.array((QPointF.x(),QPointF.y()),dtype = numpy.float)
        pixelNp = numpy.array((pixel.x(), pixel.y()), dtype=numpy.float)
        return (pixelNp - (self.translation + self.autoScaleTranslation)) * (
            1.0 / (self.scale * self.autoScale)
        )

    def inZoom(self, scale, pixel):
        position = self.QpixelToPosition(pixel)
        self.translation = (
            asNumpy(pixel) - scale * self.autoScale * position
        ) - self.autoScaleTranslation
        self.scale = scale
        self.updateTransform()
        if self.updateCurrentImage:
            self.repaint()

    def updateTransform(self):
        self._transform.reset()
        # doit être avant le scale , sinon la translation se fait dans le repère agrandit...
        self._transform.translate(
            *(self.translation + self.autoScaleTranslation).astype(int)
        )
        self._transform.scale(self.scale * self.autoScale, self.scale * self.autoScale)
        self._positionFromPixel, b = self._transform.inverted()

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

    def mousePressEvent(self, event):
        # from PlotUI ------
        self.setFocus()
        self._lastMousePixel = asNumpy(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self._movingCursor = True
            self.setXCursor(self.positionFromQPixel(event.pos())[0], emit=True)
        elif event.button() == QtCore.Qt.RightButton:
            self._movingImage = True
            self.setCursor(QtCore.Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        # from PlotUI ------
        # and not event.buttons(): # and not event.buttons() rajouté pour eviter bug sur macbook pro
        if event.button() == QtCore.Qt.RightButton:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._movingImage = False
        elif event.button() == QtCore.Qt.LeftButton:
            self._movingCursor = False
        else:
            print(event.button)

    def mouseMoveEvent(self, event):
        # from PlotUI ------
        newMousePixelI = asNumpy(event.pos())
        buttons = event.buttons()
        if buttons:
            if self._movingCursor:
                self.setXCursor(self.positionFromQPixel(event.pos())[0], emit=True)
            if self._movingImage:  # Right Button pressed
                deltaPixelI = newMousePixelI - self._lastMousePixel
                self._lastMousePixel = newMousePixelI
                self.translation = self.translation + deltaPixelI
                self.updateTransform()
                if self.updateCurrentImage:
                    self.repaint()

    def positionFromQPixel(self, QPixel):
        QPositionF = self._positionFromPixel.map(QtCore.QPointF(QPixel))
        return numpy.array((QPositionF.x(), QPositionF.y()), dtype=numpy.float)

    def paintEvent(self, event):
        if self.image is not None:
            self.updateAutoscale()
            if self._QImage is None:
                # QtGui.QImage.Format_Indexed8
                self._QImage = numpy2qimage(self.image, QImage.Format_RGB32)
            painter = QtGui.QPainter(self)
            painter.setWorldTransform(self._transform)
            if self.smooth:
                painter.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
            painter.drawImage(0, 0, self._QImage)
            if self._xCursor is not None:
                # print(self._xCursor)
                painter.setPen(self._xCursorPen)
                cursorLine = QtCore.QLineF(
                    self._xCursor, 1.0, self._xCursor, len(self.image) - 1.0
                )
                painter.drawLine(cursorLine)
                painter.end()

    # slots ------------------------

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    @QtCore.Slot(object)
    def setXCursor(self, x, emit=False):
        if x is None:
            self._xCursor = None
            self.update()
            return
        if x < self.xmin:
            x = self.xmin
        elif x > self.xmax:
            x = self.xmax
        intX = int(round(x))  # int(x+0.5) ne marche pas pour nombre negatifs !!!!
        # if self.useIntX :
        #    x = intX
        if self._xCursor != x:
            # print(x)
            # print(self._xCursor, x)
            if emit and (
                (self._xCursor is None) or (intX != int(round(self._xCursor)))
            ):
                self.outX[int].emit(intX)
            self._xCursor = x
            ##    emitIntX = False
            # self._useBufferedImage = True
            # print("update in setXCursor")
            self.update()
            # if emitIntX :
            #
            # self.outX[float].emit(x)

    @QtCore.Slot(object)
    def inImage(self, image):
        self.xmin = 0
        self.xmax = image.shape[1]
        self.image = image
        self._QImage = None
        self.update()

    def updateAutoscale(self):
        if self.autoRescale and self.image is not None:
            h, w = self.image.shape[:2]
            scaleX = float(self.height()) / h
            scaleY = float(self.width()) / w
            autoScale = min(scaleX, scaleY)
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
                print("new autoScale : ", autoScale)
                print("new autoScaleTranslation : ", self.autoScaleTranslation)
                self.updateTransform()

    @QtCore.Slot(float)
    def setScale(self, scale):
        self.__dict__["scale"] = scale
        self.updateTransform()
        if self.updateCurrentImage:
            self.update()

    @QtCore.Slot(object)
    def setTranslation(self, translation):
        self.__dict__["translation"] = translation
        self.updateTransform()
        if self.updateCurrentImage:
            self.update()

    """# serialization

    def setSerialize(self, value):
        self._serialize = value

    def getSerialize(self):
        return self._serialize
    serialize = QtCore.Property(bool, getSerialize, setSerialize)

    def setSerializeImage(self, value):
        self._serializeImage = value

    def getSerializeImage(self):
        return self._serializeImage
    serializeImage = QtCore.Property(bool, getSerializeImage, setSerializeImage)

    def __getstate__(self):
        if self._serialize:
            if self._serializeImage:
                return self.__dict__
            else:
                return remove(self.__dict__, toRemove="image")"""


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ImageShowUI()
    widget.show()
    # app.exec_()