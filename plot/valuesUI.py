from qtpy import QtGui, QtWidgets, QtCore
from math import sqrt

# from friture.plotting.scaleDivision import numberPrecision
# from friture.plotting import cmrmap

# A widget canvas with a baseline, ticks and tick labels
# The logic of the placement of scale min/max and ticks belongs to another class.
# The title belongs to another class.


class VerticalValuesUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(VerticalValuesUI, self).__init__()
        self.tickFormatter = lambda tick, digits: "{0:.{1}f}".format(tick, digits)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum
            )
        )
        self.axe = None
        self.minPen = QtGui.QPen()
        self.showMinor = False
        self.minPen.setColor(QtGui.QColor())

    def setAxe(self, axe):
        self.axe = axe
        self.updateGeometry()
        self.update()

    def sizeHint(self):
        if self.axe is not None:
            fm = QtGui.QFontMetrics(self.font())
            self.fontHeight = fm.height() / 1.5
            # print(self.axe.minorDecimal)

            # axeMinorHeight  =abs(self.axe.minorTicks[1]-self.axe.minorTicks[0])

            if self.axe.minorIntensity > 0.5:
                # axeMinorHeight - fontHeight
                # elf.axe.minorIntensity
                # print(self.axe.minorIntensity)
                # minorColor.setAlphaF(self.axe.minorIntensity)
                axeFontMinorIntensity = (self.axe.minorIntensity - 0.50) * 2.0
                self.minPen.setColor(
                    QtGui.QColor(*[0, 0, 0, axeFontMinorIntensity * 255.0])
                )
                self.showMinor = True
                self.digits = max(0, (-self.axe.minorDecimal))
                maxLabelWidth = max(
                    [
                        fm.width(self.tickFormatter(minorValue, self.digits))
                        for minorValue in self.axe.minorValues
                    ]
                )

            else:
                self.showMinor = False
                self.digits = max(0, -(self.axe.minorDecimal + 1))
                maxLabelWidth = max(
                    [
                        fm.width(self.tickFormatter(majorValue, self.digits))
                        for majorValue in self.axe.majorValues
                    ]
                )
                # maxLabelWidth += self.axe.minorIntensity*fm.width("0")*2.
            return QtCore.QSize(maxLabelWidth, 0)
        else:
            return QtCore.QSize(0, 0)

    def __getstate__(self):
        return {}

    def paintEvent(self, event):
        if self.axe is not None:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            fm = painter.fontMetrics()
            if self.showMinor:
                painter.setPen(self.minPen)
                for y, value in zip(self.axe.minorTicks, self.axe.minorValues):
                    value_string = self.tickFormatter(value, self.digits)
                    painter.drawText(
                        QtCore.QPointF(
                            self.width() - fm.width(value_string),
                            y + (self.fontHeight / 2.0),
                        ),
                        value_string,
                    )
            painter.setPen(QtGui.QColor())
            for y, value in zip(self.axe.majorTicks, self.axe.majorValues):
                value_string = self.tickFormatter(value, self.digits)
                painter.drawText(
                    QtCore.QPointF(
                        self.width() - fm.width(value_string),
                        y + (self.fontHeight / 2.0),
                    ),
                    value_string,
                )


class HorizontalValuesUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(HorizontalValuesUI, self).__init__()
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
            )
        )
        self.axe = None
        self.minPen = QtGui.QPen()
        self.showMinor = False

    def setAxe(self, axe):
        self.axe = axe
        self.updateGeometry()
        self.update()

    def sizeHint(self):
        if self.axe is not None:
            fm = QtGui.QFontMetrics(self.font())
            self.fontHeight = fm.height() / 1.5
            self.digits = max(0, -(self.axe.minorDecimal + 1))
            fm = QtGui.QFontMetrics(self.font())
            return QtCore.QSize(0, self.fontHeight)
        else:
            return QtCore.QSize(0, 0)

    def paintEvent(self, event):
        if self.axe is not None:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            fm = painter.fontMetrics()
            for x, value in zip(self.axe.majorTicks, self.axe.majorValues):
                value_string = "{0:.{1}f}".format(value, self.digits)
                painter.drawText(
                    QtCore.QPointF(x - (fm.width(value_string) / 2.0), self.fontHeight),
                    value_string,
                )
