# -*- coding: utf-8 -*-
import sys
import numpy
from qtpy import QtGui, QtCore, QtWidgets
from OpenGL.GL import glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE
from SmartFramework.ui.Trackpad import Trackpad
from SmartFramework.plot import arrayToQPath, Pen

# from SmartFramework.ui.Wacom import Wacom

# ===========================================================


# Choix de la classe de base. Ne peut pas être fait par l'application ?!   faire 3 versions ?
#
# QtWidgets.QWidget :
#   + appels à paintEvent non bloquant
#   - lent
#
# QGLWidget :
#   + beaucoup plus fluide que QtWidgets.QWidget (si vue large) sur curves avec beaucopup d'elements avec epessaire > 1.
#   - plus supporté à partir de PyQt version xxx?
#   - par contre rame completement avec gros zoom
#   - semble pouvoir provoquer des memory errors...
#   - appels bloquant à paintEvent qui granularise l'application si pas pas multi-threadé
#   => plusieurs plotUI s'inter bloquent ?!

# QtWidgets.QOpenGLWidget :
#    - pb avec text
#    - pb avec background
#    - buffeurisation
#    - appels bloquant à paintEvent qui granularise l'application ? si pas pas multi-threadé
#      => plusieurs plotUI s'inter bloquent ?!


try:
    from qtpy import QtOpenGL

    # PLOT_BASE = QtOpenGL.QGLWidget
    PLOT_BASE = QtWidgets.QWidget
except:

    class QGLWidget:
        pass

    class QtOpenGL:
        QGLWidget = QGLWidget

    # ne pas renomer (quoi ? ) pour que compilation ui -> python puisse reconnaitre init args de QWidget
    PLOT_BASE = QtWidgets.QWidget
    # PLOT_BASE = QtWidgets.QOpenGLWidget


# =============================================================

eps = numpy.finfo(numpy.float32).eps
LEFT, RIGHT, CENTRED = 0, 1, 2
X, Y = 0, 1
eps = numpy.finfo(numpy.float32).eps
debug = False


class PlotUI(PLOT_BASE, Trackpad):

    resized = QtCore.Signal(int, int)
    outNewCurve = QtCore.Signal(object)
    outClean = QtCore.Signal()  # permet de clean les menus
    outX = QtCore.Signal((int,), (float,))
    outSelectedCurve = QtCore.Signal(object)
    outSelectedCurveTitle = QtCore.Signal(str)
    outMouseOverCurveName = QtCore.Signal(str)
    outKeyEvent = QtCore.Signal(object)
    outXTranslateAndScale = QtCore.Signal(float, float)

    def __init__(
        self,
        parent=None,
        objectName="",
        antialising=True,
        ticksColor=[0, 0, 0],
        gridColor=[230, 230, 230],
        showGrid=True,
        showTicks=False,
        showBorder=True,
        borderWidth=1,
        showVerticalAxe=True,
        showHorizontalAxe=True,
        rotation=0,
        verticalAxeSide=0,
        fontSize=6,
        xWheelZoomEnableInCentralZone=True,
        yWheelZoomEnableInCentralZone=True,
        defaultXmax=1.0,
        backgroundColor=QtCore.Qt.white,
        **kwargs
    ):
        if isinstance(self, QtOpenGL.QGLWidget):
            QtOpenGL.QGLWidget.__init__(
                self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent, **kwargs
            )
        elif isinstance(self, QtWidgets.QOpenGLWidget):
            QtWidgets.QOpenGLWidget.__init__(self, parent, **kwargs)
            format_ = QtGui.QSurfaceFormat()
            format_.setSamples(8)
            self.setFormat(format_)
        else:
            QtWidgets.QWidget.__init__(self, parent, **kwargs)
        # pour version sans openGL

        # Wacom.__init__(self)
        Trackpad.__init__(self)
        self._curveEditing = None
        self._curveToUnselectAtMousseRelease = None
        # eviter de faire buger plugin qt designer qui fera appel à la proprieté
        self.__dict__["defaultXmax"] = defaultXmax
        self._oldTabletPixelHiRes = None
        self._lastMousePixel = numpy.zeros(2)
        self._ready = True
        self._buffQImage = None
        self._useBufferedImage = False
        self.antialising = antialising
        self._anyIndexedCurve = False
        if objectName is not None:
            self.setObjectName(objectName)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.MinimumExpanding,
                QtWidgets.QSizePolicy.MinimumExpanding,
            )
        )
        self._pixelFromNormalized = QtGui.QTransform()
        self._normalizedFromPosition = QtGui.QTransform()
        # calcule a partir de self._normalizedFromPosition * self._pixelFromNormalized
        self._pixelFromPosition = QtGui.QTransform()
        # calcule a partir de self._pixelFromPosition
        self._positionFromPixel = QtGui.QTransform()
        self._wheelZoomFactor = 0.0003
        self._movingImage = False
        self._showCurveValue = True
        self.setMouseTracking(self._showCurveValue)
        self._xCursor = None
        self._xCursorPen = Pen((255, 0, 0, 100), 2.0)
        self.setAutoFillBackground(True)
        self.grayBrush = QtGui.QBrush(
            QtGui.QColor(self.palette().color(QtGui.QPalette.Window)),
            QtCore.Qt.SolidPattern,
        )
        self.setBackgroundColor(backgroundColor)
        # self._updateTimer = QtCore.QTimer() # permet d'attendre d'avoir recu toutes les curves avant de faire un update
        # self._updateTimer.setSingleShot(True)
        # self._updateTimer.setInterval(10)
        # self._updateTimer.timeout.connect(self.updateWithAutoZoom )
        self._showNextCurveValueTimer = QtCore.QTimer()
        self._showNextCurveValueTimer.setSingleShot(True)
        self._showNextCurveValueTimer.setInterval(0)
        self._showNextCurveValueTimer.timeout.connect(self.showNextCurveValue)
        # self._resetLastCurveTimer = QtCore.QTimer() # permet d'attendre d'avoir recu toutes les curves avant de faire un update
        # self._resetLastCurveTimer.setSingleShot(True)
        # self._resetLastCurveTimer.setInterval(3000)
        # self._resetLastCurveTimer.timeout.connect(self.resetLastCurve)
        self._movingCursor = False
        self.clean()
        self.useIntX = True
        # self.rotation = 90.
        self.setRotation(rotation)
        self._ticksColor = ticksColor
        self._gridColor = gridColor
        self._showGrid = showGrid
        self._showTicks = showTicks
        self._showBorder = showBorder
        self._ticksUp = False
        self._ticksDown = True
        self._ticksLeft = False
        self._ticksRigth = True
        # self._ticksSides = [False,True,True,False]
        self.scaling = [True, True]
        self._selectDistanceMin = 25
        self._lastPoint = None
        self._lastCurve = None
        self._lastSelectedCurve = None
        self._titleToCoordThreshol = 25
        self._borderWidth = borderWidth
        self._margeY = 0.0
        self._margeX = 0.0
        self.xMinors = []
        self.yMinors = []
        self.xMajors = []
        self.yMajors = []
        self.showVerticalAxe = showVerticalAxe
        self.showHorizontalAxe = showHorizontalAxe
        self.verticalMinPen = QtGui.QPen()
        self.fontSize = fontSize  # pour eviter de faire planter qt desginer
        font = self.font()  # renvoie un objet different à chaque appel
        font.setPointSize(fontSize)
        self.setFont(font)
        self._font = font
        QtWidgets.QToolTip.setFont(font)
        # self.xMinPen = QtGui.QPen()
        self.fontHeight = int(
            numpy.round(QtGui.QFontMetrics(self.font()).height() / 1.5)
        )
        self.margeFont = 2
        self.verticalAxeWidth = 0
        self.verticalAxeSide = verticalAxeSide
        if verticalAxeSide == LEFT:
            self.verticalAlignement = RIGHT
        else:
            self.verticalAlignement = LEFT
        if self.showHorizontalAxe:
            self.horizontalAxeHeight = self.fontHeight + self.margeFont
        else:
            self.horizontalAxeHeight = 0
        self._xIsStr = False
        self._xWheelZoomEnableInCentralZone = xWheelZoomEnableInCentralZone
        self._yWheelZoomEnableInCentralZone = yWheelZoomEnableInCentralZone
        self._updateWithAutoZoom = False
        # self._trackerFormatter= lambda point, title: "[%.3g, %.3g]" % (point[0],point[1],title))

    def update(self):
        # print(self.objectName(), "update")
        self._ready = False
        if isinstance(self, QtOpenGL.QGLWidget):
            QtOpenGL.QGLWidget.update(self)
        elif isinstance(self, QtWidgets.QOpenGLWidget):
            QtWidgets.QOpenGLWidget.update(self)
        else:
            QtWidgets.QWidget.update(self)

    # ajout / supression de curves
    @QtCore.Slot(str, object)
    def inPlot(self, widgetName, curve):

        # print("inPlot")
        if widgetName == self.objectName():
            self.addCurve(curve)

    @QtCore.Slot(object)
    def addCurve(self, curve, autoZoom=True):
        if curve.isIndexedCurve():
            self._anyIndexedCurve = True
        # print("addCurve")
        if curve._xIsStr and curve.X != self._xStrs:
            # evite de réordonner si c'est juste que c'est la première courbe ajoutée et que self._xStrs  est vide
            if not self._xStrs:
                self._xStrs = curve.X.copy()
            else:
                for x in curve.X:
                    if x not in self._xStrs:
                        self._xStrs.append(x)
                curve.updateStringsOrder(self._xStrs)
                # for existingCurve in self.curves :
                #    existingCurve.updateStringsOrder(self._xStrs)
            self.updateMinScale()
            self.resetZoom()

        for existingCurve in self.curves:
            if (
                curve.name
                and curve.name == existingCurve.name
                and curve.trackingName == existingCurve.trackingName
            ):
                existingCurve.setData(curve.X, curve.Y, updateAttachedPlots=False)
        else:
            curve.attach(self)
            if isinstance(curve.visibleByDefault, bool):
                curve.setVisible(curve.visibleByDefault)
            self.outNewCurve.emit(curve)
        if curve._isEmpty is False:
            if curve._xIsRange is False:
                if curve.X is None:
                    raise Exception("bug")
                if not isinstance(curve.X[0], (int, numpy.int64)):
                    # idealement faudrait tester tout le tableau , mais c'est pas crucial, c'est juste pour savoir si doit afficher les subdivision #not issubclass(curve.X.dtype.type, numpy.integer):
                    self.useIntX = False
        if autoZoom:
            self.update()

    def removeCurve(self, curve):
        self.curves.remove(curve)
        if hasattr(curve, "_toRemoveIn"):
            del curve._toRemoveIn[curve._title]
        self._updateWithAutoZoom = True  # utile ?
        self.update()

    def setCurves(self, curves):
        for curve in curves:
            self.addCurve(curve, autoZoom=False)
        self.updateMinMax()
        # print("setCurveFinished")
        # self.update()
        # self.updateMinScale()

    def __getstate__(self):
        state = {}
        if self.curves != []:
            state["curves"] = [curve for curve in self.curves if curve.saveInPlot]
            if self.rotation != 0.0:
                state["rotation"] = self.rotation
            if not (self.scale == numpy.array([1.0, 1.0])).all():
                state["scale"] = self.scale
            if self.translation.any():
                state["translation"] = self.translation
        return state

    def tickFormatter(self, tick, digits):
        if isinstance(tick, str):
            return tick
        elif isinstance(tick, tuple):
            return ".".join(tick)
        else:
            return "{0:.{1}f}".format(tick, digits)

    # Methode sur données

    def setXMax(self, xmax):
        if xmax <= self.xmin:
            self.xmin = self.xmax - eps
        self.xmax = xmax
        self.updateMinScale()
        self.resetZoom()

    @QtCore.Slot()
    def clean(self):
        self._xStrs = []
        self.curves = []
        self.scale = numpy.array([1.0, 1.0])
        self.translation = numpy.array([0.0, 0.0])
        self.ymin = 0.0
        self.ymax = 1.0
        self.xmin = 0.0
        self.xmax = self.defaultXmax
        self.updateMinScale()
        # if self.objectName() == "perFrame":  print("update in clean")
        self.update()

    def updateMinMax(self, onlyVisible=True):
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        validValues = False
        for curve in self.curves:
            if curve._visible or not onlyVisible:
                validValues = True
                if (curve.xmin is not None) and (xmin is None or xmin > curve.xmin):
                    xmin = curve.xmin
                if (curve.xmax is not None) and (xmax is None or xmax < curve.xmax):
                    xmax = curve.xmax
                if (curve.ymin is not None) and (ymin is None or ymin > curve.ymin):
                    ymin = curve.ymin
                if (curve.ymax is not None) and (ymax is None or ymax < curve.ymax):
                    ymax = curve.ymax
        if validValues and xmin is not None:
            self.xmin = float(xmin)
            self.xmax = float(xmax)
            if ymin is not None:
                self.ymin = float(ymin)
                self.ymax = float(ymax)
            self.updateMinScale()

    def updateMinScale(self):
        yDelta = self.ymax - self.ymin
        if self._xStrs:
            xDelta = len(self._xStrs) - 1
        else:
            xDelta = self.xmax - self.xmin
        if yDelta == 0.0 or numpy.isnan(yDelta):
            yDelta = 1.0
        if xDelta == 0.0 or numpy.isnan(xDelta):
            xDelta = 1.0
        self.minScale = 1.0 / numpy.array([xDelta, yDelta])

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def setDefaultXmax(self, defaultXmax):
        # permet dans faceEditor de rentrer taille de la video et ainsi d'eviter que le setXCursor(180) n'emette un self.outX[int].emit(1), car le xmax vaut 1 .
        self.__dict__["defaultXmax"] = defaultXmax
        self.xmax = self.defaultXmax
        self.updateMinScale()
        self.update()

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def setXCursor(self, x):
        if x < self.xmin:
            x = self.xmin
        elif x > self.xmax:
            x = self.xmax
        intX = int(round(x))  # int(x+0.5) ne marche pas pour nombre negatifs !!!!
        if self.useIntX:
            x = intX
        if self._xCursor != x:
            # print(self._xCursor, x)
            if (self._xCursor is None) or (intX != int(round(self._xCursor))):
                self._xCursor = x  # le met là pour eviter boucle infini
                emitIntX = True
            else:
                self._xCursor = x
                emitIntX = False
            self._useBufferedImage = True
            # print("update in setXCursor")
            self.update()
            if emitIntX:
                self.outX[int].emit(intX)
            self.outX[float].emit(x)

    def setXCursorOrSelectCurve(self, QPixel):
        # print("setXCursorOrSelectCurve")
        self._curveToUnselectAtMousseRelease = None
        nextCurve, nextPoint, nextIndex = self.nextCurvePointIndex(
            QPixel, self._selectDistanceMin
        )
        if nextCurve is None:
            position = self.positionFromQPixel(QPixel)
            self._movingCursor = True
            self.setXCursor(position[0])
        else:
            if nextCurve.editable:
                self._curveEditingIndex = nextIndex
                self._curveEditing = nextCurve
            if nextCurve._selected:
                self._curveToUnselectAtMousseRelease = nextCurve
            else:
                if self._lastSelectedCurve is not None:
                    self._lastSelectedCurve.setSelected(False)
                nextCurve.setSelected(True)
                self._lastSelectedCurve = nextCurve
                self.outSelectedCurve.emit(nextCurve)

    def resetLastCurve(self):
        # print("resetLastCurve")
        # fou un peu la merde si y' des NaN sur un curves, car réaffiche à chaque fois le nom de la curve quand il la retrouve, en en meme temps intererer à le laisser pour pouvoir réafficher nom de la courbe si on s'eloigne et reviens dessus:
        self._lastCurve = None

    def showNextCurveValueLowPriority(self, QPixel):
        # print("showNextCurveValueLowPriority")
        self._nextQPixel = QPixel
        self._showNextCurveValueTimer.stop()
        self._showNextCurveValueTimer.start()

    def showNextCurveValue(self):
        # print("showNextCurveValue")
        QPixel = self._nextQPixel
        nextCurve, nextPoint, nextIndex = self.nextCurvePointIndex(
            QPixel, self._selectDistanceMin, priorityToUnderlined=True
        )
        if nextCurve is None:
            if QtWidgets.QToolTip.isVisible():
                QtWidgets.QToolTip.hideText()
            # if not self._resetLastCurveTimer.isActive() and self._lastCurve is not None:
            #   #print "start timer"
            #    self._resetLastCurveTimer.start()
            # fou un peu la merde si y' des NaN sur un curves, car réaffiche à chaque fois le nom de la curve quand il la retrouve, en en meme temps intererer à le laisser pour pouvoir réafficher nom de la courbe si on s'eloigne et reviens dessus:
            self._lastCurve = None

        else:
            # recuper la vraie position du/des points (plutot que de la souris )
            globalPixel = self.globalPixelFromPosition(nextPoint)
            printedStr = ""
            if self._lastCurve != nextCurve:
                self._lastCurve = nextCurve
                printedStr = "\n".join(nextCurve.name) + "\n"
                newCurve = True
            else:
                newCurve = False
            if (
                newCurve
                or self._lastPoint is None
                or (self._lastCurveToolTipLocation is None)
                or (
                    numpy.linalg.norm(asNumpy(self._lastCurveToolTipLocation - QPixel))
                    > self._titleToCoordThreshol
                )
            ):
                x, y = nextPoint
                if nextCurve._xIsStr:
                    x = nextCurve.X[nextIndex]
                    if isinstance(x, tuple):
                        x = ".".join(x)
                    printedStr += "%.3g\n%s" % (y, x)
                elif nextCurve._xIsRange:
                    printedStr += "y:%.3g\nx:%d" % (y, x)
                else:
                    printedStr += "y:%.3g\nx:%.3g" % (y, x)
                if nextCurve.Z is not None:
                    z = nextCurve.Z[nextIndex]
                    if z != -1:
                        if nextCurve.zTranslate is not None:
                            z = nextCurve.zTranslate[z]
                        printedStr += "\n%s" % str(z)
                if newCurve:
                    self._lastCurveToolTipLocation = QPixel
                    self.outMouseOverCurveName.emit(nextCurve._title)
                else:
                    self._lastCurveToolTipLocation = None
                QtWidgets.QToolTip.showText(globalPixel, printedStr)
            self._lastPoint = nextPoint

    def nextCurvePointIndex(
        self, QPixel, distanceThresold=30, priorityToUnderlined=False
    ):
        nextUnderlinedPixelDistance = distanceThresold
        nextPixelDistance = distanceThresold
        nextCurvePointIndex = (None, None, None)
        for curve in self.curves:
            if curve._visible and not curve._isEmpty:
                (
                    nearPoint,
                    nearIndex,
                    nearPixelDistance,
                ) = curve.findNearPointIndexsAndPixelDistance(
                    QPixel, self._positionFromPixel
                )
                if nearPixelDistance is not numpy.NaN:
                    if curve.pen.bold:
                        if nearPixelDistance < nextPixelDistance or (
                            priorityToUnderlined
                            and nearPixelDistance < nextUnderlinedPixelDistance
                        ):
                            nextUnderlinedPixelDistance = (
                                nextPixelDistance
                            ) = nearPixelDistance
                            nextCurvePointIndex = (curve, nearPoint, nearIndex)
                    else:
                        if nearPixelDistance < nextPixelDistance:
                            if not priorityToUnderlined or (
                                nextUnderlinedPixelDistance == distanceThresold
                            ):
                                nextPixelDistance = nearPixelDistance
                                nextCurvePointIndex = (curve, nearPoint, nearIndex)
        # print(nextPixelDistance)
        return nextCurvePointIndex

    # conversions pixel <-> coordonnées

    def positionFromQPixel(self, QPixel):
        QPositionF = self._positionFromPixel.map(QtCore.QPointF(QPixel))
        return numpy.array((QPositionF.x(), QPositionF.y()), dtype=float)

    def positionFromPixel(self, pixel):  # A OPTIMISER !!!!!!
        QPixel = QtCore.QPointF(*pixel)
        QPositionF = self._positionFromPixel.map(QPixel)
        return numpy.array((QPositionF.x(), QPositionF.y()), dtype=float)

    def positionFromNormalized(self, normalized):  # A OPTIMISER !!!!!!
        QPixel = QtCore.QPointF(*normalized)
        QPositionF = self._normalizedFromPosition.inverted()[0].map(QPixel)
        return numpy.array((QPositionF.x(), QPositionF.y()), dtype=float)

    def normalizedFromPixel(self, pixel):  # A OPTIMISER !!!!!
        if numpy.iterable(pixel):
            QpixelF = QtCore.QPointF(*pixel)
        else:
            QpixelF = QtCore.QPointF(pixel)
        QPositionF = self._normalizedFromPixel.map(QpixelF)
        return numpy.array((QPositionF.x(), QPositionF.y()), dtype=float)

    def pixelFromGlobalPixel(self, globalPixel):
        # pour etre compatible avec pyqt6 et pyqt5
        return globalPixel - QtCore.QPointF(self.mapToGlobal(QtCore.QPoint()))

    def positionFromGlobalPixel(self, globalPixel):
        QPixelF = QtCore.QPointF(*globalPixel) - QtCore.QPointF(
            self.mapToGlobal(QtCore.QPoint())
        )
        QPointF = self._positionFromPixel.map(QPixelF)
        return numpy.array((QPointF.x(), QPointF.y()), dtype=float)

    def globalPixelFromPosition(self, position):
        QPixelF = self._pixelFromPosition.map(QtCore.QPointF(*position))
        globalPixelF = QPixelF + QtCore.QPointF(self.mapToGlobal(QtCore.QPoint()))
        return QtCore.QPoint(int(round(globalPixelF.x())), int(round(globalPixelF.y())))

    # affichage ------------------------------------------

    """@QtCore.Slot()      
    def updateLowPriority(self):  
        # if self.objectName() == "perFrame":  print("updateLowPriority")
        self._updateTimer.stop()
        self._updateTimer.start()  """

    def setAntialiasing(self, b):
        if self.antialising != b:
            self.antialising = b
            # print("update in setAntialiasing")
            # if self.objectName() == "perFrame":  print("update in antialising")
            self.update()

    def paintEvent(self, event):
        # if self.objectName() == "perAnimation":  print("paintEvent")
        # print(self.objectName(), "paintEvent")
        self.updateWithAutoZoom()
        if self._useBufferedImage and self._buffQImage is not None:
            painter = QtGui.QPainter(self)
            # if self.objectName() == "perAnimation": print("use buffered QImage")
            if isinstance(self, (QtOpenGL.QGLWidget, QtWidgets.QOpenGLWidget)):
                painter.drawImage(QtCore.QPoint(), self._buffQImage)
            else:  # version sans openGL
                painter.drawPixmap(QtCore.QPoint(), self._buffQImage)
            self._useBufferedImage = False
        else:
            # print("paint Event")
            """if self.objectName() == "perAnimation":
            print("repaint image because")
            if self._useBufferedImage is False :
                print("self._useBufferedImage is False")
            if self._buffQImage is None :
                print("self._buffQImage is None")"""

            if (
                not isinstance(self, (QtOpenGL.QGLWidget, QtWidgets.QOpenGLWidget))
                and self._useBufferedImage
            ):
                # version sans OpenGL
                self._buffQImage = QtGui.QPixmap(self.size())
                self._buffQImage.fill()
                painter = QtGui.QPainter(self._buffQImage)
                painter.setFont(self._font)
            else:
                painter = QtGui.QPainter(self)
                if isinstance(self, QtWidgets.QOpenGLWidget):
                    painter.fillRect(self.rect(), self.palette().window())

            if self.antialising:
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
            if self._showGrid:
                self.drawGrid(painter)
            if self._showTicks:
                self.drawTicks(painter)
            if self._showBorder:
                self.drawBorder(painter)
            self.drawData(painter, drawIndexedCurve=False)
            if self.verticalAxeSide == LEFT:
                painter.fillRect(
                    0, 0, self.verticalAxeWidth, self.height(), self.grayBrush
                )
            else:
                painter.fillRect(
                    self.width() - self.verticalAxeWidth,
                    0,
                    self.verticalAxeWidth,
                    self.height(),
                    self.grayBrush,
                )
            painter.fillRect(
                0,
                self.height() - self.horizontalAxeHeight,
                self.width(),
                self.height(),
                self.grayBrush,
            )
            self.paintVerticalValues(painter)
            self.paintHorizontalValues(painter)
            if self._useBufferedImage:
                if isinstance(self, (QtOpenGL.QGLWidget, QtWidgets.QOpenGLWidget)):
                    # version OpenGL :  la bufferisation doit se faire avant drawCursor, on ne peut la faire ailleur
                    self.bufferQImage()
                else:  # version sans OpenGL
                    painter = QtGui.QPainter(self)
                    painter.drawPixmap(QtCore.QPoint(), self._buffQImage)
                self._useBufferedImage = False
            else:
                self._buffQImage = None

        if self.antialising:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if self._anyIndexedCurve:
            if self.verticalAxeSide == LEFT:
                x = self.verticalAxeWidth
            else:
                x = 0
            painter.setClipRect(
                x,
                0,
                self.width() - self.verticalAxeWidth,
                self.height() - self.horizontalAxeHeight,
            )
            self.drawData(painter, drawIndexedCurve=True)
        self.drawCursor(painter)
        painter.end()
        self._ready = True

    def drawCursor(self, painter):
        painter.setWorldTransform(self._pixelFromPosition)
        # QPixelF = self._pixelFromPosition.map(QtCore.QPointF(*position))
        # pixel = self._xCursor
        xCursor = self._xCursor
        visibleXmin, visibleYmin = self.positionFromNormalized([0.0, 0.0])
        visibleXmax, visibleYmax = self.positionFromNormalized([1.0, 1.0])
        if (
            (xCursor is not None)
            and (visibleXmin <= xCursor)
            and (xCursor <= visibleXmax)
        ):
            painter.setPen(self._xCursorPen)
            cursorLine = QtCore.QLineF(
                self._xCursor, visibleYmin, self._xCursor, visibleYmax
            )
            painter.drawLine(cursorLine)

    def setBackgroundColor(self, color):
        if numpy.iterable(color):
            color = QtGui.QColor(*color)
        self._backgroundColor = color
        p = self.palette()
        p.setColor(p.Window, color)
        self.setPalette(p)

    def getBackgroundColor(self):
        return self._backgroundColor

    def bufferQImage(self):
        """Read the current buffer pixels out as a QImage."""
        w = self.width()
        h = self.height()
        glPixels = numpy.empty((h, w, 4), dtype=numpy.ubyte)
        glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, glPixels)
        # swap B,R channels and flip vertical for Qt
        bgrx = numpy.empty((h, w, 4), dtype=numpy.ubyte)
        bgrx[..., 0] = glPixels[::-1, :, 2]
        bgrx[..., 1] = glPixels[::-1, :, 1]
        bgrx[..., 2] = glPixels[::-1, :, 0]
        bgrx[..., 3] = glPixels[::-1, :, 3]
        img = QtGui.QImage(bgrx.data, w, h, QtGui.QImage.Format_ARGB32)
        img.data = bgrx
        self._buffQImage = img

    def updateMinorAndMajorTickAxe(self, axe):
        cornerPositions = [
            self.positionFromNormalized(corner)
            for corner in [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        ]
        visibleMin = numpy.minimum.reduce(cornerPositions)[axe]
        visibleMax = numpy.maximum.reduce(cornerPositions)[axe]
        if axe == X:
            if (self.rotation) % 180 == 0:
                nbPixelPerUnit = abs(
                    self.scale[axe] * (self.width() - self.verticalAxeWidth)
                )
            else:
                nbPixelPerUnit = abs(
                    self.scale[axe] * (self.height() - self.horizontalAxeHeight)
                )
        else:  # axe == Y:
            if (self.rotation) % 180 == 0:
                nbPixelPerUnit = abs(
                    self.scale[axe] * (self.height() - self.horizontalAxeHeight)
                )
            else:
                nbPixelPerUnit = abs(
                    self.scale[axe] * (self.width() - self.verticalAxeWidth)
                )
        if nbPixelPerUnit == 0.0:
            return  # evite plantage , a approfondir?
        nPixelMinPerBar = 5
        minorMinimumDecimal = numpy.log10(nPixelMinPerBar / nbPixelPerUnit)

        if self.useIntX and axe == 0:
            minorMinimumDecimal = max(
                minorMinimumDecimal, -1
            )  # ca marche sans trop savoir exactement pourquoi
        majorMinimumDecimal = minorMinimumDecimal + 1

        for minimumDecimal, minor in [
            (majorMinimumDecimal, False),
            (minorMinimumDecimal, True),
        ]:
            decimal = int(numpy.ceil(minimumDecimal))
            if minor:
                minorDecimal = decimal
                if axe == 0:
                    self.xMinorGreyIntensity = decimal - minimumDecimal
                    self.xMinorDecimal = minorDecimal
                else:
                    self.yMinorGreyIntensity = decimal - minimumDecimal
                    self.yMinorDecimal = minorDecimal
            puissance = 10 ** (-int(decimal))
            firstBarValue = numpy.ceil(visibleMin * puissance)
            lastBarValue = numpy.ceil(visibleMax * puissance + eps)
            barValues = (
                numpy.arange(firstBarValue, lastBarValue) / puissance
            )  # coordonnées barres dans repere des curves (positions)

            # barValues[barValues==0.] = 0. # force les 0. a etre positifs et non pas -0.

            if axe == X:
                if (self.rotation) % 180 == 0:
                    pixelCoord = [
                        self._pixelFromPosition.map(value, 0.0)[0]
                        for value in barValues
                    ]
                else:
                    pixelCoord = [
                        self._pixelFromPosition.map(value, 0.0)[1]
                        for value in barValues
                    ]
                if minor:
                    self.xMinors = pixelCoord
                    if self._xStrs:
                        self.xMinorValues = [
                            self._xStrs[int(barIndex)] for barIndex in barValues
                        ]
                    else:
                        self.xMinorValues = barValues
                else:
                    self.xMajors = pixelCoord
                    if self._xStrs:
                        self.xMajorValues = [
                            self._xStrs[int(barIndex)] for barIndex in barValues
                        ]
                    else:
                        self.xMajorValues = barValues
            else:
                if (self.rotation) % 180 == 0:
                    pixelCoord = [
                        self._pixelFromPosition.map(0.0, value)[1]
                        for value in barValues
                    ]
                else:
                    pixelCoord = [
                        self._pixelFromPosition.map(0.0, value)[0]
                        for value in barValues
                    ]
                if minor:
                    self.yMinors = pixelCoord
                    self.yMinorValues = barValues
                else:
                    self.yMajors = pixelCoord
                    self.yMajorValues = barValues

    def updateMinorAndMajorTick(self):
        # appeller plein de fois au lancement à cause de multiples resizes()
        # dans repere des points,pour suporter roation
        if self.width() and self.height():
            if (self.rotation) % 180 == 0:
                self.updateMinorAndMajorTickAxe(Y)
                self.updateVerticalAxe()
                self.updateMinorAndMajorTickAxe(X)
                self.updateHorizontalAxe()
            else:
                self.updateMinorAndMajorTickAxe(X)
                self.updateVerticalAxe()
                self.updateMinorAndMajorTickAxe(Y)
                self.updateHorizontalAxe()

    def updateVerticalAxe(self):
        if self.showVerticalAxe:
            fm = QtGui.QFontMetrics(self.font())
            if (self.rotation) % 180 == 0:
                verticalMinorGreyIntensity = self.yMinorGreyIntensity
                verticalMinorDecimal = self.yMinorDecimal
                verticalMinorValues = self.yMinorValues
                verticalMajorValues = self.yMajorValues
            else:
                verticalMinorGreyIntensity = self.xMinorGreyIntensity
                verticalMinorDecimal = self.xMinorDecimal
                verticalMinorValues = self.xMinorValues
                verticalMajorValues = self.xMajorValues
            if verticalMinorGreyIntensity > 0.4:
                axeFontMinorIntensity = (verticalMinorGreyIntensity - 0.40) * (
                    1.0 / 0.6
                )
                self.verticalMinPen.setColor(
                    QtGui.QColor(*[0, 0, 0, int(axeFontMinorIntensity * 255)])
                )
                self.verticalShowMinor = True
                self.verticalDigits = max(0, (-verticalMinorDecimal))
                verticalprintedMinorValues = [
                    self.tickFormatter(minorValue, self.verticalDigits)
                    for minorValue in verticalMinorValues
                ]
                if verticalprintedMinorValues:
                    newVerticalAxeWidht = (
                        max([fm.width(elt) for elt in verticalprintedMinorValues])
                        + 2 * self.margeFont
                    )
                else:
                    newVerticalAxeWidht = 0.0
            else:
                self.verticalShowMinor = False
                self.verticalDigits = max(0, -(verticalMinorDecimal + 1))
                verticalprintedValues = [
                    self.tickFormatter(majorValue, self.verticalDigits)
                    for majorValue in verticalMajorValues
                ]
                if verticalprintedValues:
                    newVerticalAxeWidht = (
                        max([fm.width(elt) for elt in verticalprintedValues])
                        + 2 * self.margeFont
                    )
                else:
                    newVerticalAxeWidht = 0
        else:
            newVerticalAxeWidht = 0
        if self.verticalAxeWidth != newVerticalAxeWidht:
            self.verticalAxeWidth = newVerticalAxeWidht
            self.updatePixelVsNormalized()

    def updateHorizontalAxe(self):
        if self.showHorizontalAxe:
            if (self.rotation) % 180 == 0:
                horizontalMinorDecimal = self.xMinorDecimal
            else:
                horizontalMinorDecimal = self.yMinorDecimal
            self.horizontalDigits = max(0, -(horizontalMinorDecimal + 1))
            self.horizontalAxeHeight = self.fontHeight + self.margeFont
        else:
            self.horizontalAxeHeight = 0

    def paintVerticalValues(self, painter):
        if (self.rotation) % 180 == 0:
            verticalMinors = self.yMinors
            verticalMajors = self.yMajors
            verticalMinorValues = self.yMinorValues
            verticalMajorValues = self.yMajorValues
        else:
            verticalMinors = self.xMinors
            verticalMajors = self.xMajors
            verticalMinorValues = self.xMinorValues
            verticalMajorValues = self.xMajorValues

        if self.showVerticalAxe:
            fm = painter.fontMetrics()
            for verticalPixels, verticalValues, minor in [
                (verticalMajors, verticalMajorValues, False),
                (verticalMinors, verticalMinorValues, True),
            ]:
                if minor:
                    if not self.verticalShowMinor:
                        continue
                    elif self._xStrs:
                        painter.setPen(QtGui.QColor())
                    else:
                        painter.setPen(self.verticalMinPen)
                else:
                    painter.setPen(QtGui.QColor())
                for verticalPixel, value in zip(verticalPixels, verticalValues):
                    if not minor or value not in verticalMajorValues:
                        value_string = self.tickFormatter(value, self.verticalDigits)
                        verticalPixel = numpy.clip(
                            verticalPixel + (self.fontHeight / 2.0),
                            self.fontHeight,
                            self.height(),
                        )
                        if self.verticalAxeSide == LEFT:
                            if self.verticalAlignement == CENTRED:
                                horizontalPixel = (
                                    self.verticalAxeWidth - fm.width(value_string)
                                ) / 2.0
                            elif self.verticalAlignement == RIGHT:
                                horizontalPixel = (
                                    self.verticalAxeWidth
                                    - self.margeFont
                                    - fm.width(value_string)
                                )
                            elif self.verticalAlignement == LEFT:
                                horizontalPixel = self.margeFont
                            painter.drawText(
                                QtCore.QPointF(horizontalPixel, verticalPixel),
                                value_string,
                            )

                        else:
                            if self.verticalAlignement == CENTRED:
                                horizontalPixel = (
                                    self.width()
                                    - (self.verticalAxeWidth + fm.width(value_string))
                                    / 2.0
                                )
                            elif self.verticalAlignement == RIGHT:
                                horizontalPixel = (
                                    self.width()
                                    - fm.width(value_string)
                                    - self.margeFont
                                )
                            elif self.verticalAlignement == LEFT:
                                horizontalPixel = (
                                    self.width()
                                    - self.verticalAxeWidth
                                    + self.margeFont
                                )
                            painter.drawText(
                                QtCore.QPointF(horizontalPixel, verticalPixel),
                                value_string,
                            )

    def paintHorizontalValues(self, painter):
        painter.setPen(QtGui.QColor())
        if (self.rotation) % 180 == 0:
            horizontalMajors = self.xMajors
            horizontalMajorValues = self.xMajorValues
        else:
            horizontalMajors = self.yMajors
            horizontalMajorValues = self.yMajorValues
        if self.showHorizontalAxe:
            fm = painter.fontMetrics()
            for horizontalPixel, value in zip(horizontalMajors, horizontalMajorValues):
                value_string = self.tickFormatter(value, self.horizontalDigits)
                stringWidth = fm.width(value_string)
                horizontalPixel = numpy.clip(
                    horizontalPixel - (stringWidth / 2.0), 0, self.width() - stringWidth
                )
                painter.drawText(
                    QtCore.QPointF(horizontalPixel, self.height()), value_string
                )

    def setGridColor(self, color):
        self.__dict__["gridColord"] = color

    def setTicksColor(self, color):
        self.__dict__["ticksColor"] = color

    def drawGrid(self, painter):
        painter.setWorldTransform(QtGui.QTransform())
        if (self.rotation) % 180 == 0:
            verticalMinors = self.yMinors
            verticalMajors = self.yMajors
            verticalMinorGreyIntensity = self.yMinorGreyIntensity
            horizontalMinors = self.xMinors
            horizontalMajors = self.xMajors
            horizontalMinorGreyIntensity = self.xMinorGreyIntensity
        else:
            verticalMinors = self.xMinors
            verticalMajors = self.xMajors
            verticalMinorGreyIntensity = self.xMinorGreyIntensity
            horizontalMinors = self.yMinors
            horizontalMajors = self.yMajors
            horizontalMinorGreyIntensity = self.yMinorGreyIntensity
        verticalMin = 0
        verticalMax = self.height()
        horizontalMin = 0
        horizontalMax = self.width()
        penGrid = Pen()
        penGrid.setColor(self._gridColor)
        greyIntensity = horizontalMinorGreyIntensity
        penGrid.setOppacity(greyIntensity)
        painter.setPen(penGrid)
        for horizontalMinor in horizontalMinors:
            painter.drawLine(
                QtCore.QLineF(
                    horizontalMinor, verticalMin, horizontalMinor, verticalMax
                )
            )
        greyIntensity = verticalMinorGreyIntensity
        penGrid.setOppacity(greyIntensity)
        painter.setPen(penGrid)
        for verticalMinor in verticalMinors:
            painter.drawLine(
                QtCore.QLineF(
                    horizontalMin, verticalMinor, horizontalMax, verticalMinor
                )
            )
        penGrid.setOppacity(1.0)
        painter.setPen(penGrid)
        for horizontalMajor in horizontalMajors:
            painter.drawLine(
                QtCore.QLineF(
                    horizontalMajor, verticalMin, horizontalMajor, verticalMax
                )
            )
        for verticalMajor in verticalMajors:
            painter.drawLine(
                QtCore.QLineF(
                    horizontalMin, verticalMajor, horizontalMax, verticalMajor
                )
            )
            pass

    def drawBorder(self, painter):
        painter.setWorldTransform(QtGui.QTransform())
        painter.setPen(Pen(self._ticksColor, self._borderWidth * 2.0))
        if self.verticalAxeSide == LEFT:
            painter.drawRect(
                self.verticalAxeWidth,
                0,
                self.width() - self.verticalAxeWidth,
                self.height() - self.horizontalAxeHeight,
            )
        else:
            painter.drawRect(
                0,
                0,
                self.width() - self.verticalAxeWidth,
                self.height() - self.horizontalAxeHeight,
            )

    def drawTicks(self, painter):
        # dessine les tick
        painter.setWorldTransform(QtGui.QTransform())
        if (self.rotation) % 180 == 0:
            verticalMinors = self.yMinors
            verticalMajors = self.yMajors
            verticalMinorGreyIntensity = self.yMinorGreyIntensity
            horizontalMinors = self.xMinors
            horizontalMajors = self.xMajors
            horizontalMinorGreyIntensity = self.xMinorGreyIntensity
        else:
            verticalMinors = self.xMinors
            verticalMajors = self.xMajors
            verticalMinorGreyIntensity = self.xMinorGreyIntensity
            horizontalMinors = self.yMinors
            horizontalMajors = self.yMajors
            horizontalMinorGreyIntensity = self.yMinorGreyIntensity
        width = self.width()
        height = self.height()
        penTick = Pen(2.0)
        majorTickWidth = 10.0
        penTick.setColor(self._ticksColor)
        greyIntensity = horizontalMinorGreyIntensity
        penTick.setOppacity(greyIntensity)
        painter.setPen(penTick)
        MinorTickWidth = majorTickWidth * greyIntensity
        for horizontalMinor in horizontalMinors:
            if self._ticksLeft:
                painter.drawLine(
                    QtCore.QLineF(horizontalMinor, 0.0, horizontalMinor, MinorTickWidth)
                )
            if self._ticksRigth:
                painter.drawLine(
                    QtCore.QLineF(
                        horizontalMinor,
                        height - MinorTickWidth,
                        horizontalMinor,
                        height,
                    )
                )
        penTick.setOppacity(1.0)
        painter.setPen(penTick)
        for horizontalMajor in horizontalMajors:
            if self._ticksLeft:
                painter.drawLine(
                    QtCore.QLineF(horizontalMajor, 0.0, horizontalMajor, majorTickWidth)
                )
            if self._ticksRigth:
                painter.drawLine(
                    QtCore.QLineF(
                        horizontalMajor,
                        height - majorTickWidth,
                        horizontalMajor,
                        height,
                    )
                )

        greyIntensity = verticalMinorGreyIntensity
        penTick.setOppacity(greyIntensity)
        painter.setPen(penTick)
        MinorTickWidth = majorTickWidth * greyIntensity
        for verticalMinor in verticalMinors:
            if self._ticksUp:
                painter.drawLine(
                    QtCore.QLineF(0.0, verticalMinor, MinorTickWidth, verticalMinor)
                )
            if self._ticksDown:
                painter.drawLine(
                    QtCore.QLineF(
                        width - MinorTickWidth, verticalMinor, width, verticalMinor
                    )
                )
        penTick.setOppacity(1.0)
        painter.setPen(penTick)
        for verticalMajor in verticalMajors:
            if self._ticksUp:
                painter.drawLine(
                    QtCore.QLineF(0.0, verticalMajor, majorTickWidth, verticalMajor)
                )
            if self._ticksDown:
                painter.drawLine(
                    QtCore.QLineF(
                        width - majorTickWidth, verticalMajor, width, verticalMajor
                    )
                )

    def drawData(self, painter, drawIndexedCurve):
        # if self.objectName() == "perFrame": print("drawData")
        painter.setWorldTransform(self._pixelFromPosition)
        for curve in self.curves:
            if curve._visible and (curve.isIndexedCurve() is drawIndexedCurve):
                curve.draw(
                    painter
                )  # , self.horizontalScaleTransform, self.verticalScaleTransform, self.rect()
                # print(self.objectName())
                # if self.objectName() == "perFrame":print(curve._title)
        painter.setWorldTransform(QtGui.QTransform())

    def getTicksColor(self):
        return self._ticksColor

    ticksColor = QtCore.Property(list, getTicksColor, setTicksColor)

    def getGridColor(self):
        return self._gridColor

    gridColor = QtCore.Property(list, getGridColor, setGridColor)

    def setShowGrid(self, value):
        self._showGrid = value

    def getShowGrid(self):
        return self._showGrid

    showGrid = QtCore.Property(bool, getShowGrid, setShowGrid)

    def setShowTicks(self, value):
        self._showTicks = value

    def getShowTicks(self):
        return self._showTicks

    showTicks = QtCore.Property(bool, getShowTicks, setShowTicks)

    def setShowBorder(self, value):
        self._showBorder = value

    def getShowBorder(self):
        return self._showBorder

    showBorder = QtCore.Property(bool, getShowBorder, setShowBorder)

    def setBorderWidth(self, value):
        self._borderWidth = value

    def getBorderWidth(self):
        return self._borderWidth

    borderWidth = QtCore.Property(int, getBorderWidth, setBorderWidth)

    # Zoom

    def inZoom(self, scale, pixel):
        scale = numpy.maximum(scale, self.minScale)
        if (self.scale != scale).any():
            position = self.positionFromQPixel(pixel)
            normalized = self.normalizedFromPixel(pixel)
            self.scale = scale
            self.setTranslation(normalized - scale * position)
            self.updateTransform()
            # print("update in inZoom")
            # if self.objectName() == "perFrame":  print("update in zoom")
            self.update()

    def addPixelTranslation(self, pixelTranslation):
        addedTranslation = self._normalizedFromPixelDelta.map(
            QtCore.QPointF(*pixelTranslation)
        )  # / numpy.array([self.width(),-self.height()])
        addedTranslation = numpy.array(
            (addedTranslation.x(), addedTranslation.y()), dtype=float
        )
        translation = self.translation + addedTranslation
        return self.setTranslation(translation)

    def setRotation(self, rotation):
        self.__dict__["rotation"] = rotation
        if (self.rotation) % 180 == 0:
            self.horizontalAxe = X
            self.verticalAxe = Y
        else:
            self.horizontalAxe = Y
            self.verticalAxe = X
        # self.update() # A REVOIR

    @QtCore.Slot(object)
    def setTranslation(self, translation):
        # imageSize = numpy.array(self._image.shape[::-1])
        scaledImageSize = numpy.array([self.xmax, self.ymax]) * self.scale
        minTranslation = numpy.array([1.0, 1.0]) - scaledImageSize
        maxTranslation = (
            -numpy.array([self.xmin, self.ymin]) * self.scale
        )  # numpy.array([self.xmax,self.ymax]) * self.scale
        translation = translation.clip(minTranslation, maxTranslation)
        if (self.__dict__["translation"] != translation).any():
            # print(self.__dict__['translation'] - translation)
            self.__dict__["translation"] = translation
            return True
        else:
            return False  # dit de ne pas updater
        # self.updateTransform()
        # self.updateLowPriority()

    @QtCore.Slot(object)
    def setScale(self, scale):
        """n'est utilisé que par la déserialisation?"""
        # widgetQsize = self.size()
        # widgetSize = numpy.array((widgetQsize.width(),widgetQsize.height()),dtype = numpy.float)

        # imageSize = numpy.array(self.xmax,self.ymax)
        # scaledImageSize = imageSize * self.scale
        # maxTranslation = [0,0]
        # self.__dict__['translation'] = translation.clip(minTranslation,maxTranslation)
        self.__dict__["scale"] = scale
        # self.updateTransform()
        # self.updateLowPriority()

    def updateWithAutoZoom(self):
        if self._updateWithAutoZoom:
            # if self.objectName() == "perFrame":  print("updateWithAutoZoom")

            cornerPositions = [
                self.positionFromNormalized(corner)
                for corner in [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
            ]
            visibelMinX, visibleMinY = numpy.minimum.reduce(cornerPositions)
            visibleMaxX, visibleMaxY = numpy.maximum.reduce(cornerPositions)
            reset = False
            if all(self.scale == self.minScale):
                # pass
                reset = True
            self.updateMinMax(onlyVisible=True)
            if (
                (visibelMinX < self.xmin)
                or (self.xmax < visibleMaxX)
                or (visibleMinY < self.ymin)
                or (self.ymax < visibleMaxY)
            ):
                reset = True
            if reset:
                # print("resetZoom")
                self.resetZoom()
            else:
                self.updateMinorAndMajorTick()
            # else :
            # print("update in updateWithAutoZoom")
            # if self.objectName() == "perFrame":  print("update in updateWithAutoZoom")
            #    self.update()
            # self.updateMinMax(onlyVisible = True)
        self._updateWithAutoZoom = False

    def resetZoomToVisible(self):
        self.updateMinMax(onlyVisible=True)
        self.resetZoom()

    def resetZoom(self):
        self.scale = self.minScale
        self.translation = numpy.array([-self.xmin, -self.ymin]) * self.scale
        self.updateTransform()
        # print("update in resetZoom")
        # if self.objectName() == "perFrame":  print("update in resetZoom")
        # self.update()

    def updateTransform(self, xTranslateAndScaleEmit=True):
        # print("updateTransform")
        self._normalizedFromPosition.reset()
        self._normalizedFromPosition.translate(
            *self.translation
        )  # doit etre avant le scale , car on veut faire translation dans repère visualisé et non dans repère image d'origine, sinon la translation se fait dans le repère agrandit...
        self._normalizedFromPosition.scale(*self.scale)  #
        self._pixelFromPosition = (
            self._normalizedFromPosition * self._pixelFromNormalized
        )
        self._positionFromPixel, b = self._pixelFromPosition.inverted()
        self.updateMinorAndMajorTick()
        if xTranslateAndScaleEmit:
            self.outXTranslateAndScale.emit(self.translation[0], self.scale[0])

    @QtCore.Slot(float, float)
    def setXTranslateAndScale(self, xTranslate, xScale):
        if self.translation[0] != xTranslate or self.scale[0] != xScale:
            self.translation[0] = xTranslate
            self.scale[0] = xScale
            self.updateTransform(xTranslateAndScaleEmit=False)
            self.update()

    # interface souris et tablette graphique
    def wheelEvent(self, event):
        try:
            deltaPixel = event.angleDelta().y()  # PyQt5
        except:
            deltaPixel = event.delta()  # PyQt4 & PySide2
        delta = self._wheelZoomFactor * deltaPixel
        newScale = numpy.copy(self.scale)
        if (self.rotation) % 180 == 0:
            horizontalWheelZoomEnableInCentralZone = self._xWheelZoomEnableInCentralZone
            verticalWheelZoomEnableInCentralZone = self._yWheelZoomEnableInCentralZone
        else:
            horizontalWheelZoomEnableInCentralZone = self._yWheelZoomEnableInCentralZone
            verticalWheelZoomEnableInCentralZone = self._xWheelZoomEnableInCentralZone
        if event.buttons() & QtCore.Qt.RightButton or self.eventInHorizontalAxe(event):
            newScale[self.horizontalAxe] = self.scale[self.horizontalAxe] * (1 + delta)
        elif event.buttons() & QtCore.Qt.LeftButton or self.eventInVerticalAxe(event):
            newScale[self.verticalAxe] = self.scale[self.verticalAxe] * (1 + delta)
        else:
            # wheel dans zone central sans boutons , par defaut zoom sur les deux axes
            if (
                verticalWheelZoomEnableInCentralZone
                and horizontalWheelZoomEnableInCentralZone
            ):
                newScale = self.scale * (1 + delta)
            elif horizontalWheelZoomEnableInCentralZone:
                newScale[self.horizontalAxe] = self.scale[self.horizontalAxe] * (
                    1 + delta
                )
            elif verticalWheelZoomEnableInCentralZone:
                newScale[self.verticalAxe] = self.scale[self.verticalAxe] * (1 + delta)

        self.inZoom(newScale, event.pos())
        event.accept()

    def eventInHorizontalAxe(self, event):
        return event.pos().y() >= self.height() - self.horizontalAxeHeight

    def eventInVerticalAxe(self, event):
        if self.verticalAxeSide == LEFT:
            return event.pos().x() <= self.verticalAxeWidth
        else:
            return event.pos().x() >= self.width() - self.verticalAxeWidth

    def keyPressEvent(self, event):
        if event.key() in (
            QtCore.Qt.Key_Right,
            QtCore.Qt.Key_Left,
            QtCore.Qt.Key_Down,
            QtCore.Qt.Key_Up,
            QtCore.Qt.Key_Space,
        ):
            self.outKeyEvent.emit(event)

    def mousePressEvent(self, event):
        # print("mousePressEvent")
        self.setFocus()
        self._lastMousePixel = asNumpy(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if debug:
                print("\nmousePressLeft", end=" ")
            # position = self.positionFromQPixel()
            # self._movingCursor = True
            self.setXCursorOrSelectCurve(event.pos())
            # self.scaling = [True,False]
        elif event.button() == QtCore.Qt.RightButton:

            if debug:
                print("\nmousePressRight", end=" ")
            self._movingImage = True
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            # self.scaling[0] = False
            # self.scaling = [False,True]

    def mouseReleaseEvent(self, event):
        if (
            event.button() == QtCore.Qt.RightButton
        ):  # and not event.buttons(): # and not event.buttons() rajouté pour eviter bug sur macbook pro
            if debug:
                print("\nmouseReleaseRight", end=" ")
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._movingImage = False
            # self.butonPressed[0] = False
        elif event.button() == QtCore.Qt.LeftButton:
            if debug:
                print("\nmouseReleaseLeft", end=" ")
            self._movingCursor = False
            self._curveEditing = None
            if self._curveToUnselectAtMousseRelease is not None:
                self._curveToUnselectAtMousseRelease.setSelected(False)
                self._lastSelectedCurve = None
                self.outSelectedCurve.emit(None)
        else:
            print(event.button)
            # self.scaling[0] = True

    def mouseMoveEvent(self, event):
        # print(".")
        newMousePixelI = asNumpy(event.pos())
        buttons = event.buttons()
        if buttons:
            if self._curveEditing is not None:
                self._curveToUnselectAtMousseRelease = None
                curve = self._curveEditing
                position = self._positionFromPixel.map(QtCore.QPointF(event.pos()))
                # nearIndex,x = curve.findNearIndexsAndX(position)
                # curve.Y[nearIndex] = position.y()
                lastValue = curve.Y[self._curveEditingIndex]
                if not numpy.isnan(lastValue):
                    newValue = position.y()
                    if newValue < curve.forcedYMin:
                        newValue = curve.forcedYMin
                    elif newValue > curve.forcedYMax:
                        newValue = curve.forcedYMax
                    if lastValue != newValue:
                        if curve._rearange:
                            if curve.editInPlace == False:
                                curve._notRearangedY = curve._notRearangedY.copy()
                            curve._notRearangedY[
                                curve._rearangeNewToOldIndexs[self._curveEditingIndex]
                            ] = newValue
                        elif curve.editInPlace == False:
                            curve._notRearangedY = curve.Y = curve.Y.copy()
                        curve.Y[self._curveEditingIndex] = newValue
                        curve.update()
                        # self.edited.emit()
                        self._updateWithAutoZoom = False
                        # self._useBufferedImage = True
                        self.update()
                        if curve.editCallback is not None:
                            curve.editCallback(curve._notRearangedY)

            if self._movingCursor:
                newPosition = self.positionFromQPixel(event.pos())[0]
                # visibleXmin = self.positionFromNormalized([0.,0.])[0]
                # visibleXmax = self.positionFromNormalized([1.,0.])[0]
                # newPosition = numpy.clip(newPosition,visibleXmin,visibleXmax)
                self.setXCursor(newPosition)
            if self._movingImage:  # Right Button pressed
                deltaPixelI = newMousePixelI - self._lastMousePixel
                self._lastMousePixel = newMousePixelI
                if self.eventInHorizontalAxe(event):
                    deltaPixelI[Y] = 0.0
                if self.eventInVerticalAxe(event):
                    deltaPixelI[X] = 0.0
                if self.addPixelTranslation(deltaPixelI):
                    self.updateTransform()
                    # print("update in mouseMoveEvent")
                    # if self.objectName() == "perFrame":  print("update in mouseMoveEvent (translation)")
                    self.update()
        else:
            if self._showCurveValue and (self._lastMousePixel - newMousePixelI).any():
                self.showNextCurveValueLowPriority(event.pos())

    def touchEvent(self, event):
        # print("t",)
        newMousePixelI = asNumpy(event.pos())
        deltaPixelI = newMousePixelI - self._lastMousePixel
        if self.rect().adjusted(100, 100, -100, -100).contains(event.pos()):
            self._lastMousePixel = newMousePixelI
        else:
            self.setCursorPixel(
                self._lastMousePixel
            )  # remet la souris au point d'origine , mapToGlobal sert à passer des coordonnées % fenetre => % ecran , et QtCore.QPoint(*asNumpy car mapToGlobal n'admet pas les QPointF        s
        if self.addPixelTranslation(deltaPixelI):
            self.updateTransform()
            # if self._cursor != QtCore.Qt.BlankCursor:
            #    self.setCursor(QtCore.Qt.BlankCursor)
            # print("update in touchEvent")
            # if self.objectName() == "perFrame":  print("update in touchEvent")
            self.update()

    def setCursorPixel(self, pixel):
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(*pixel)))
        # remet la souris au point d'origine , mapToGlobal sert à passer des coordonnées % fenetre => % ecran , et QtCore.QPoint(*asNumpy car mapToGlobal n'admet pas les QPointF

    def tabletEvent(self, event):
        newPosition = asNumpy(event.pos())

        if event.type() == QtCore.QEvent.TabletMove:
            pressure = event.pressure()
            newTabletPixelHiRes = asNumpy(event.globalPosF())
            if self._ready:
                if pressure > 0.0:
                    # print("TabletMove with pressure")
                    if self._movingCursor:
                        position = self.positionFromGlobalPixel(newTabletPixelHiRes)
                        self.setXCursor(position[0])
                    if self._movingImage:
                        if self._oldTabletPixelHiRes is not None:
                            deltaPixelI = (
                                newTabletPixelHiRes - self._oldTabletPixelHiRes
                            )
                            self._oldTabletPixelHiRes = newTabletPixelHiRes
                            if self.addPixelTranslation(deltaPixelI):
                                self.updateTransform()
                                # print("update in tabletEvent")
                                # if self.objectName() == "perFrame":  print("update in tabletEvent")
                                self.update()

                elif (
                    self._showCurveValue and (newPosition != self._lastMousePixel).any()
                ):
                    self.showNextCurveValueLowPriority(event.pos())
                self._oldTabletPixelHiRes = newTabletPixelHiRes
        elif event.type() == QtCore.QEvent.TabletPress:
            # print("tablePress")
            self._lastMousePixel = asNumpy(event.pos())
            if event.button() == QtCore.Qt.RightButton:
                # print("RightButton > _movingImage")
                self._movingImage = True
                self.setCursor(QtCore.Qt.ClosedHandCursor)
            else:
                self.setXCursorOrSelectCurve(event.pos())  # pas besoin ?
        elif event.type() == QtCore.QEvent.TabletRelease:
            # print("tableRelease")
            if event.button() == QtCore.Qt.RightButton:
                self.setCursor(QtCore.Qt.ArrowCursor)
                self._movingImage = False
            else:
                self._movingCursor = False
        self._lastMousePixel = newPosition
        self.setFocus()

    def updatePixelVsNormalized(self):

        self._pixelFromNormalized.reset()
        # scale = min(self.width(),self.height())
        # les transformation sont ecrite dans l'ordre inverse
        if self._showBorder:
            borderWidth = self._borderWidth
        else:
            borderWidth = 0.0
        if (self.rotation) % 180 == 0:
            width = (
                self.width()
                - 2 * borderWidth
                - 2 * self._margeX
                - self.verticalAxeWidth
            )
            height = (
                self.height()
                - 2 * borderWidth
                - 2 * self._margeY
                - self.horizontalAxeHeight
            )
            if self.verticalAxeSide == LEFT:
                self._pixelFromNormalized.translate(
                    width * 0.5 + self.verticalAxeWidth + self._margeX + borderWidth,
                    height * 0.5 + self._margeY + borderWidth,
                )  # decentre
            else:
                self._pixelFromNormalized.translate(
                    width * 0.5 + self._margeX + borderWidth,
                    height * 0.5 + self._margeY + borderWidth,
                )  # decentre
        else:
            width = (
                self.width()
                - 2 * borderWidth
                - 2 * self._margeY
                - self.verticalAxeWidth
            )
            height = (
                self.height()
                - 2 * borderWidth
                - 2 * self._margeX
                - self.horizontalAxeHeight
            )
            if self.verticalAxeSide == LEFT:
                self._pixelFromNormalized.translate(
                    width * 0.5 + self.verticalAxeWidth + self._margeY + borderWidth,
                    height * 0.5 + self._margeX + borderWidth,
                )  # decentre
            else:
                self._pixelFromNormalized.translate(
                    width * 0.5 + self._margeY + borderWidth,
                    height * 0.5 + self._margeX + borderWidth,
                )  # decentre

        self._pixelFromNormalized.scale(width, height)  # agrandi
        self._pixelFromNormalized.rotate(self.rotation)  # fait rotation
        self._pixelFromNormalized.translate(-0.5, 0.5)  # recentre en zero
        self._pixelFromNormalized.scale(1.0, -1.0)  # redresse en inversant les y
        self._normalizedFromPixel = (
            normalizedFromPixel
        ) = self._pixelFromNormalized.inverted()[0]
        self._normalizedFromPixelDelta = QtGui.QTransform(
            normalizedFromPixel.m11(),
            normalizedFromPixel.m12(),
            normalizedFromPixel.m21(),
            normalizedFromPixel.m22(),
            0.0,
            0.0,
        )
        self.updateTransform()

    def resizeEvent(self, event):
        if self.width() and self.height():
            self.updatePixelVsNormalized()
            self.resized.emit(self.width(), self.height())
            # print("update in resizeEvent")
            # if self.objectName() == "perFrame":  print("update in resizeEvent")
            self.update()


class Axe:
    def __init__(
        self,
        majorTicks,
        majorValues,
        minorTicks,
        minorValues,
        minorDecimal,
        minorIntensity,
    ):
        self.majorTicks = majorTicks
        self.majorValues = majorValues
        self.minorTicks = minorTicks
        self.minorValues = minorValues
        self.minorDecimal = minorDecimal
        self.minorIntensity = minorIntensity


class Curve(object):
    # http://stackoverflow.com/questions/13632919/how-to-implement-optional-first-argument-in-python-reproduce-slice-behavior
    # def __init__(self, y,name,pen = None,trackingName = None,visibleByDefault = True):

    def __reduce__(self):
        initArgs = [
            self._notRearangedX,
            self._notRearangedY,
            self.name,
            self.pen,
            self.trackingName,
            self.visibleByDefault,
            self._notRearangedZ,
            self.zTranslate,
            self.saveInPlot,
            self.indexedDataPath,
            self.forcedYMin,
            self.forcedYMax,
            self.editable,
            self.editInPlace,
            self.editCallbackPath,
        ]
        # remove from end if default value
        initArgsEndDefaults = [
            None,
            None,
            None,
            True,
            None,
            None,
            True,
            None,
            None,
            None,
            False,
            True,
            None,
        ]
        for defaultValue in reversed(initArgsEndDefaults):
            if defaultValue == initArgs[-1]:
                del initArgs[-1]
            else:
                break
        return self.__class__, tuple(initArgs)

    def __init__(
        self,
        x,
        y,
        name=None,
        pen=None,
        trackingName=None,
        visibleByDefault=True,
        z=None,
        zTranslate=None,
        saveInPlot=True,
        indexedDataPath=None,
        yMin=None,
        yMax=None,
        editable=False,
        editInPlace=True,
        editCallbackPath=None,
        penColor=None,
        editCallback=None,
    ):
        """x peut etre mis à None, pour correpondre automatiquement aux indices de y
        x peut egalement etre une liste de string"""
        self.saveInPlot = saveInPlot
        self.editCallback = editCallback
        self.editInPlace = editInPlace
        self.editCallbackPath = editCallbackPath
        self.indexedDataPath = indexedDataPath
        self._plots = []
        self.forcedYMin = yMin
        self.forcedYMax = yMax
        self.editable = editable
        self._visible = None

        self._useQPoly = False  # True 15x plus rapide d'utiliser QPath que Qpoly !!!
        if isinstance(name, str):
            name = [name]
        elif name is None:
            name = []
        self.name = name
        self._title = ".".join([elt for elt in [trackingName] + name if elt])
        if not pen:
            self.pen = Pen()
        else:
            self.pen = pen  # le stock pour pouvoir le modifier
        if penColor is not None:
            self.pen.setColor(penColor)

        self.setData(x, y, z, zTranslate)
        self.trackingName = trackingName
        self.visibleByDefault = visibleByDefault

        self.pen.setCosmetic(True)
        self._selected = False
        self._underline = False
        self._rearange = False
        # self._xIsStr = None # merdi pour test ...on ne met pas à False car on ne sait encore rien
        # self._xIsRange = None # on n'en sait encore rien
        self._mustCreateNewPoly = True
        self._QPath = None  # leasy evaluation

    def isIndexedCurve(self):
        return self.indexedDataPath is not None

    def plots(self):
        # pour voir meme interface que  QwtPlotCurve, j'ai juste mis une liste au lieu d'un seul plot
        return self._plots

    def attach(self, plot):  # pour voir meme interface que  QwtPlotCurve
        self._plots.append(plot)
        plot.curves.append(self)

    def addData(self, x, y, updateAttachedPlots=True):
        X = self.X
        Y = self.Y
        if x is None:
            if X is None:
                pass
            else:
                if self._xIsRange:
                    x = X[-1] + 1
                else:
                    raise Exception("unable to add None x to existing not range self.X")
        elif X is None:
            raise Exception("unable to add  x to existing None X")
        elif isinstance(x, (str, tuple)):
            if self._xIsStr is False:
                raise Exception(
                    "ajout d'un x string à une coubre dont les x ne sont pas des string"
                )
            else:
                self._xIsStr = True

        if x is not None:
            X.append(x)
            if X is not self._notRearangedX:
                self._notRearangedX.append(x)
        Y.append(y)
        if Y is not self._notRearangedY:
            self._notRearangedY.append(y)
        self.n += 1
        self._isEmpty = False

        if x is None or self._xIsStr:
            self.xmax = self.n - 1
            # self._xIsRange = True   # a priori vaut déjà true si le Y lors de l'initialisation etait vide
        else:
            self.xmax = x
            # self.xmax = max(self.xmax,x)
            # self.xmin = min(self.xmin,x)
            # if x == 0 and self.n == 1  :
            #    self._xIsRange = True # a priori vaut déjà true si le Y lors de l'initialisation etait vide
            if self._xIsRange and x != X[-1] + 1:
                self._xIsRange = False
                if self._plots:
                    for plot in self._plots:
                        plot.useIntX = False
        if y is None or y == numpy.NaN:
            self._mustCreateNewPoly = True

        else:
            if self._useQPoly:
                if self._mustCreateNewPoly:
                    self._QPolys.append(QtGui.QPolygonF())
                self._QPolys[-1] << QtCore.QPointF(x, y)
            else:
                if self._mustCreateNewPoly:
                    self._QPath.moveTo(x, y)
                else:
                    self._QPath.lineTo(x, y)
            self._mustCreateNewPoly = False
            self.ymin = min(self.ymin, y)
            self.ymax = min(self.ymax, y)
        if updateAttachedPlots:
            for plot in self._plots:
                plot._updateWithAutoZoom = True
                plot.update()
        # else :
        #    self.update()

    def updateDataY(self, Y):

        if Y is None:
            self.Y = numpy.full(self.n, numpy.nan)
            if self._rearange:
                self._notRearangedY = numpy.full(len(self._notRearangedX), numpy.nan)
            else:
                self._notRearangedY = self.Y
        else:
            # print("updateDataY")
            if self._rearange:
                self._notRearangedY = Y
                self.Y = self.rearanged(Y)
            else:
                self._notRearangedY = self.Y = Y
        # sorti pour pouvoir faire appel à meme fonction dans self.addData(x,y):
        self.update()
        for plot in self._plots:
            plot._updateWithAutoZoom = False
            plot._useBufferedImage = True
            plot.update()

    def setData(self, X, Y, Z=None, zTranslate=None, updateAttachedPlots=True):
        if (X is not None) and (len(X) != len(Y)):
            raise Exception("len(X) != len(Y)")
        self._notRearangedX = self.X = X
        self._notRearangedY = self.Y = Y
        self._notRearangedZ = self.Z = Z
        self.zTranslate = zTranslate
        # print("update in setData")
        # sorti pour pouvoir faire appel à meme fonction dans self.addData(x,y):
        self.update()
        if updateAttachedPlots:
            for plot in self._plots:
                plot._updateWithAutoZoom = True
                plot.update()

    def rearanged(self, notRearangedY):
        new = numpy.full(self.n, numpy.NaN)
        if isinstance(notRearangedY, list):
            notRearangedY = numpy.array(notRearangedY)
        new[self._rearangeNewIndexs] = notRearangedY[self._rearangeOldIndexs]
        return new

    def updateStringsOrder(self, xStrs):
        """en vrai , il ne faudrait pas toucher à self.x, mais uniquemnt aux QPolys ?  ne poserait pas problème pour la recherche du point voisin de la souris?"""
        oldIndexs = []
        newIndexs = []
        newToOldIndexs = []
        for newIndex, xStr in enumerate(xStrs):
            if xStr in self._notRearangedX:
                oldIndex = self._notRearangedX.index(xStr)
                oldIndexs.append(oldIndex)
                newIndexs.append(newIndex)
                newToOldIndexs.append(oldIndex)
            else:
                newToOldIndexs.append(None)
        self._rearangeOldIndexs = numpy.array(oldIndexs)
        self._rearangeNewIndexs = numpy.array(newIndexs)
        # sert à editer à la fois Y et _notRearangedY dans PlotUI.mousseMoveEvent
        self._rearangeNewToOldIndexs = newToOldIndexs
        self._rearange = True
        self.n = len(xStrs)
        self.X = xStrs.copy()
        self.Y = self.rearanged(self._notRearangedY)
        if self._notRearangedZ is not None:
            self.Z = self.rearanged(self._notRearangedZ)
        # sorti pour pouvoir faire appel à meme fonction dans self.addData(x,y):
        self.update()
        for plot in self._plots:
            plot._updateWithAutoZoom = False
            plot.update()

        # self.setData(list(xStrs),self.rearangeY(self.Y))

    # @profile
    def update(self):  #
        # print(self.objectName() ,"update" )
        X = self.X
        Y = self.Y
        self._xIsStr = False  # valeur par defaut
        self.n = len(Y)
        # compute xmin,xmax,ymin,ymax (for zoom limits and auto-scaling)
        if len(Y) == 0:
            self.xmin = None
            self.xmax = None
            self.ymin = self.forcedYMin
            self.ymax = self.forcedYMax
            self._QPolys = []
            self._QPath = False
            self._isEmpty = True
            self._xIsRange = True
        else:
            self._isEmpty = False
            if X is None or isinstance(X[0], (str, tuple)):
                if X is not None:
                    self._xIsStr = True
                self.xmin = 0
                self.xmax = self.n - 1
                # je n'ecrase pas les string protentiellement dans self.X, mais semble servir pour la suite si y'a des NaN dans le Y

                self._xIsRange = True
            else:
                # numpy.nanmin(X)  # on autorise les x à ne pas etre croissants ?
                self.xmin = X[0]
                # numpy.nanmax(X)  # on autorise les x à ne pas etre croissants ?
                self.xmax = X[-1]
                self._xIsRange = isRange(X)
            # on ne stock pas pour Yisnan pour eviter de prendre trop de mémoire?
            Yisnan = numpy.isnan(Y)

            if numpy.all(Yisnan):
                # problem si que des nan dans Y , self.ymin et self.ymax sont mis à nan
                self.ymin = self.forcedYMin
                self.ymax = self.forcedYMax
                self._QPolys = []
                self._QPath = False
            else:
                if self.forcedYMin is not None:
                    self.ymin = self.forcedYMin
                else:
                    self.ymin = numpy.nanmin(Y)
                if self.forcedYMax is not None:
                    self.ymax = self.forcedYMax
                else:
                    self.ymax = numpy.nanmax(Y)

                if self._useQPoly:
                    if numpy.isnan(numpy.sum(Y)):
                        splitedCurves = [
                            (X[s], Y[s])
                            for s in numpy.ma.clump_unmasked(numpy.ma.masked_invalid(Y))
                        ]
                    else:
                        splitedCurves = [(X, Y)]
                    self._QPolys = [
                        QtGui.QPolygonF([QtCore.QPointF(*point) for point in zip(*XY)])
                        for XY in splitedCurves
                    ]
                elif self._visible:
                    # print("update")
                    # 1 msec pour 10000 elts :
                    if X is None or self._xIsStr:
                        X = numpy.arange(self.n)
                    self._QPath = arrayToQPath(X, Y, connect=~Yisnan)
                else:
                    self._QPath = None

    def setVisible(self, b):
        if b != self._visible:
            self._visible = b
            for plot in self._plots:
                plot._updateWithAutoZoom = True
                plot.update()

    def setSelected(self, b):
        # quand click sur un coube ou la selectionne dans curveSelecot, normalement il y en a qu'une seule de selectionnée , et elle reste en bold, meme quand un met underline à False
        self._selected = b
        self.updateBoldAndOppactity()

    def setUnderline(self, b):  # tracking selectionné dans trackingSelectorUI
        self._underline = b
        self.updateBoldAndOppactity()

    def updateBoldAndOppactity(self):
        if self._selected:
            oppacity, bold = 1.0, True
        elif self._underline:
            oppacity, bold = 0.7, 0.3
        else:
            oppacity, bold = 0.4, False
        if (oppacity, bold) != (self.pen.oppacity, self.pen.bold):
            self.pen.setOppacity(oppacity)
            self.pen.setBold(bold)
            for plot in self._plots:
                # print("update in updateBold")
                # pass
                # if plot.objectName() == "perFrame":  print("update in updateBold")
                plot.update()

    def setColor(self, color):
        # if self.pen is not None :
        if not isinstance(color, QtGui.QColor):
            color = QtGui.QColor(*color)
        if color != self.pen.color():
            self.pen.setColor(color)  # sock la couleure
            for plot in self._plots:
                # print("update in setColor")
                # pass
                # if plot.objectName() == "perFrame":  print("update in setColor")
                # au lieu de update() car doit laisser le temps de faire un autozoom avant update() s'il faut:
                plot.update()

    def setStyle(self, QtStyle):
        if QtStyle != self.pen.style():
            self.pen.setStyle(QtStyle)
            for plot in self._plots:
                # print("update in setStyle")
                # pass
                # if plot.objectName() == "perFrame":  print("update in setStyle")
                # au lieu de update() car doit laisser le temps de faire un autozoom avant update() s'il faut:
                plot.update()

    # def setVisibleUnderlineColorSens(self,visible,underline,color,sens):
    #    self.setVisible(visible)
    #    #if self.pen is not None :
    #    self.pen.bold(underline)
    #    self.pen.setColor(QtGui.QColor(*color))  # sock la couleure
    #    if sens == -1:
    #        self.pen.setStyle(Qt.DotLine)
    # self.setPen(self.pen)

    def __getstate__(
        self,
    ):  # a utiliser si serialize en json .  je retourne rien avec serializejson, car utiliserait plus de caracteres avec ecriture de "instance(....)"
        return None

    # si sans Open GL

    def draw(self, painter):
        painter.setPen(self.pen)
        if self._useQPoly:
            for poly in self._QPolys:
                if poly.size() == 1:
                    painter.drawPoints(poly)
                else:
                    painter.drawPolyline(poly)
        elif self._QPath is not False:
            if self._QPath is None:  # leasy evaluation

                if self.X is None or self._xIsStr:
                    X = numpy.arange(self.n)
                else:
                    X = self.X
                self._QPath = arrayToQPath(X, self.Y, connect=~numpy.isnan(self.Y))
                # 1 msec pour 10000 elts

            painter.drawPath(self._QPath)

    def findNearIndexsAndX(self, position):
        # problème avec les NaN ...
        if self._isEmpty:
            return None
        if self._xIsRange:
            x = index = numpy.clip(int(round(position.x())), 0, self.n - 1)
        else:
            if type(self.X) is numpy.array:
                index = numpy.argmin(abs(self.X - position.x()))
                x = self.X[index]
            else:
                for index, x in enumerate(self.X):
                    if position.x() < x:
                        break
        return index, x

    def findNearPointIndexsAndPixelDistance(self, QPixel, positionFromPixel):
        QPixelF = QtCore.QPointF(QPixel)
        # sans QtCore.QPointF sort des entiers... :
        position = positionFromPixel.map(QPixelF)

        # problème avec les NaN ...
        if self._isEmpty:
            return None, None, None
        index, x = self.findNearIndexsAndX(position)
        nextPoint = numpy.array([x, self.Y[index]])
        if x < position.x():
            indexLeft = index
            indexRight = index + 1
        else:
            indexLeft = index - 1
            indexRight = index
        if indexLeft >= 0 and indexRight < self.n:
            if self._xIsRange:
                xLeft = indexLeft
                xRigth = indexRight
            else:
                xLeft = self.X[indexLeft]
                xRigth = self.X[indexRight]
            pointLeft = numpy.array([xLeft, self.Y[indexLeft]])
            pointRigth = numpy.array([xRigth, self.Y[indexRight]])
            pixel = asNumpy(QPixelF)
            pixelLeft = asNumpy(
                positionFromPixel.inverted()[0].map(QtCore.QPointF(*pointLeft))
            )
            pixelRight = asNumpy(
                positionFromPixel.inverted()[0].map(QtCore.QPointF(*pointRigth))
            )
            distance = distanceSegment(pixelLeft, pixelRight, pixel)
        else:
            nextPixel = positionFromPixel.inverted()[0].map(QtCore.QPointF(*nextPoint))
            distance = numpy.linalg.norm(asNumpy(QPixelF - nextPixel))

        # galère à gerer scale different en x et y et rotation ...
        # squareDistances = (self.X - position[0])**2 * scale[0] + (self.Y - position[1])**2
        # index = numpy.nanargmin(squareDistances)
        # distance = numpy.sqrt(squareDistances[index])
        return nextPoint, index, distance


def distanceSegment(A, B, C):
    """calcule la distance du point C au segment AB"""
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C
    if x1 != x2 or y1 != y2:

        px = x2 - x1
        py = y2 - y1
        something = px * px + py * py
        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)
        # u correspond à position relative [0-1] de la projection du point C sur le segment AB
        if u > 1:
            u = 1
        elif u < 0:
            u = 0
        x = x1 + u * px
        y = y1 + u * py
    else:
        # les points 1 et 2 sont confondus
        x = x1
        y = y1
    dx = x - x3
    dy = y - y3
    # Note: If the actual distance does not matter,
    # if you only want to compare what this function
    # returns to other results of this function, you
    # can just return the squared distance instead
    # (i.e. remove the sqrt) to gain a little performance
    dist = numpy.sqrt(dx * dx + dy * dy)
    return dist


def minmax(value, minimum, maximum):
    return min(max(value, minimum), maximum)


def isRange(array):
    return numpy.array_equal(array, numpy.arange(len(array)))


def asNumpy(QPointF):
    return numpy.array((QPointF.x(), QPointF.y()), dtype=float)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    # plotUI = PlotUI(antialising = True,rotation = 90,verticalAxeSide = LEFT)
    plotUI = PlotUI(antialising=True, verticalAxeSide=LEFT)
    x = numpy.linspace(0.00, 10, 1000)
    plotUI.addCurve(Curve(x, numpy.cos(x), editable=True))
    plotUI.addCurve(Curve(x, numpy.sin(x), editable=True))

    # x = ["nicolas","andre","julie","sophie","bertrand","noemie"]
    # y = [10,4,7,9,2,4]
    # x = numpy.arange(10000)
    # y = numpy.random.rand(10000)
    # plotUI.addCurve(Curve(x,y))
    plotUI.resize(QtCore.QSize(1000, 500))
    plotUI.show()

    app.exec_()  # pas besoin si on n'utilise pas de signaux