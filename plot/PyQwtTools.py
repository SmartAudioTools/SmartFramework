# from qtpy.Qt import *

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QColor, QPen, QFont  # ,Font
from qtpy.Qwt5 import (
    QwtPlot,
    QwtSymbol,
    QwtPlotCurve,
    QwtScaleEngine,
    QwtText,
    QwtLinearScaleEngine,
    QwtLog10ScaleEngine,
)  # ,


# Qt.GlobalColor aliases
Black = Qt.black
Blue = Qt.blue
Cyan = Qt.cyan
DarkBlue = Qt.darkBlue
DarkCyan = Qt.darkCyan
DarkGray = Qt.darkGray
DarkGreen = Qt.darkGreen
DarkMagenta = Qt.darkMagenta
DarkRed = Qt.darkRed
DarkYellow = Qt.darkYellow
Gray = Qt.gray
Green = Qt.green
LightGray = Qt.lightGray
Magenta = Qt.magenta
Red = Qt.red
White = Qt.white
Yellow = Qt.yellow

# Qt.PenStyle aliases
NoLine = Qt.NoPen
SolidLine = Qt.SolidLine
DashLine = Qt.DashLine
DotLine = Qt.DotLine
DashDotLine = Qt.DashDotLine
DashDotDotLine = Qt.DashDotDotLine

# QwtPlot.Axis aliases
Y1 = Left = QwtPlot.yLeft
Y2 = Right = QwtPlot.yRight
X1 = Bottom = QwtPlot.xBottom
X2 = Top = QwtPlot.xTop
axis = {
    "Left": QwtPlot.yLeft,
    "Right": QwtPlot.yRight,
    "Bottom": QwtPlot.xBottom,
    "Top": QwtPlot.xTop,
}

# QwtScaleEngine aliases
Lin = QwtLinearScaleEngine
Log = QwtLog10ScaleEngine

# QwtScaleEngine.Attribute aliases
NoAttribute = QwtScaleEngine.NoAttribute
IncludeReference = QwtScaleEngine.IncludeReference
Symmetric = QwtScaleEngine.Symmetric
Floating = QwtScaleEngine.Floating
Inverted = QwtScaleEngine.Inverted

# QwtSymbol.Style aliases
NoSymbol = QwtSymbol.NoSymbol
Circle = QwtSymbol.Ellipse
Square = QwtSymbol.Rect
Diamond = QwtSymbol.Diamond


symbols = {
    "NoSymbol": QwtSymbol.NoSymbol,
    "Circle": QwtSymbol.Ellipse,
    "Square": QwtSymbol.Rect,
    "Diamond": QwtSymbol.Diamond,
}
symbolToString = {
    QwtSymbol.NoSymbol: "NoSymbol",
    QwtSymbol.Ellipse: "Circle",
    QwtSymbol.Rect: "Square",
    QwtSymbol.Diamond: "Diamond",
}


class Curve(QwtPlotCurve):
    def __init__(
        self,
        x,
        y,
        name,
        pen=None,
        symbol=None,
        trackingName=None,
        xAxis="Bottom",
        yAxis="Left",
        visibleByDefault=True,
    ):
        if isisntance(name, str):
            name = [name]
        title = "_".join([elt for elt in [trackingName] + name if elt])
        QwtPlotCurve.__init__(self, title)
        self.setAxis(axis.get(xAxis, xAxis), axis.get(yAxis, yAxis))
        self.pen = pen  # le stock pour pouvoir le modifier
        # if pen :
        #    self.setPen(pen)
        # else:
        #    self.setStyle(QwtPlotCurve.NoCurve)
        if not pen:
            self.pen = Pen()
        self.setPen(self.pen)

        self.symbolString = symbol
        if symbol:
            self.setSymbol(symbol)

        if isinstance(x[0], str):
            print(
                "pour l'instant ne sais pas afficher courbe avec des noms en absisse regarder CPUplot.py pour exemple"
            )
        else:
            self.setData(x, y)
        self.name = name
        self.trackingName = trackingName
        # self.subName = subName
        # self.categorie = categorie
        # self.subCategorie = subCategorie
        self.xVect = x  # pas trouve comment y acceder dans le QwtPlotCurve
        self.yVect = y  # pas trouve comment y acceder dans le QwtPlotCurve
        self.visibleByDefault = visibleByDefault

    # def setPen(self): # fout la merde
    #    pass

    def __reduce__(self):
        return self.__class__, (
            self.xVect,
            self.yVect,
            self.name,
            self.pen,
            self.symbolString,
            self.trackingName,
            self.xAxis(),
            self.yAxis(),
            self.visibleByDefault,
        )

    def setStyle(self, QtStyle):
        self.pen.setStyle(QtStyle)
        self.setPen(self.pen)

    def setColor(self, color):
        # if self.pen is not None :
        self.pen.setColor(QColor(*color))  # sock la couleure
        self.setPen(self.pen)

    def underline(self, b):
        # if self.pen is not None :
        print("underline", b)
        self.pen.bold(b)
        self.setPen(self.pen)

    def setVisibleUnderlineColorSens(self, visible, underline, color, sens):
        self.setVisible(visible)
        # if self.pen is not None :
        self.pen.bold(underline)
        self.pen.setColor(QColor(*color))  # sock la couleure
        if sens == -1:
            self.pen.setStyle(Qt.DotLine)
        self.setPen(self.pen)


class Axis:
    """A command line interpreter friendly class.

    The interpretation of the `*rest` parameters is type dependent:

    - `QwtPlot.Axis`: sets the orientation of the axis.
    - `QwtScaleEngine`: sets the axis type (Lin or Log).
    - `int` : sets the attributes of the axis.
    - `string` or `QString`: sets the title of the axis.
    """

    def __init__(self, *rest):
        self.attributes = NoAttribute
        self.engine = QwtLinearScaleEngine
        self.title = QwtText("")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.title.setFont(font)

        for item in rest:
            if isinstance(item, QwtPlot.Axis):
                self.orientation = item
            elif item in [Lin, Log]:
                self.engine = item
            elif isinstance(item, int):
                self.attributes = item
            elif isinstance(item, str):  # or isinstance(item, QString)):
                self.title.setText(item)
            else:
                print(("Axis() fails to accept %s." % item))

    # __init__()


# class Axis


class Symbol(QwtSymbol):
    """A command line friendly layer over `QwtSymbol`.

    The interpretation of the `*rest` parameters is type dependent:

    - `QColor` or `Qt.GlobalColor`: sets the symbol fill color.
    - `QwtSymbol.Style`: sets symbol style.
    - `int`: sets the symbol size.
    """

    def __init__(self, *rest):
        QwtSymbol.__init__(self)
        self.setSize(5)
        for item in rest:
            if isinstance(item, (QColor, Qt.GlobalColor)):
                brush = self.brush()
                brush.setColor(item)
                self.setBrush(brush)
            elif isinstance(item, QwtSymbol.Style):
                self.setStyle(item)
            elif isinstance(item, int):
                self.setSize(item)
            else:
                print(("Symbol fails to accept %s." % item))

    # __init__()


# class Symbol


class Pen(QPen):
    """A command line friendly layer over `QPen`.

    The interpretation of the `*rest` parameters is type dependent:

    - `Qt.PenStyle`: sets the pen style.
    - `QColor` or `Qt.GlobalColor`: sets the pen color.
    - `int`: sets the pen width.
    """

    def __init__(self, *rest):
        QPen.__init__(self)
        for item in rest:
            if isinstance(item, Qt.PenStyle):
                self.setStyle(item)
            elif isinstance(item, (QColor, Qt.GlobalColor)):
                self.setColor(item)
            elif isinstance(item, int):
                self.setWidth(item)
            elif isinstance(item, float):
                self.setWidthF(item)
            else:
                print(("Pen fails to accept %s." % item))
        self.originalWidth = self.widthF()

    def bold(self, b):
        if b:
            self.setWidth(self.originalWidth * 3.0)
        else:
            self.setWidth(self.originalWidth)

    # __init__()


# class Pen
