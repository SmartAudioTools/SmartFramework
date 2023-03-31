import numpy


class Extrapol:
    def __init__(self):
        # self.fifo =
        self._lastValue = None

    def inValue(self, value):
        if self._lastValue is None:
            extrapoled = value
        else:
            extrapoled = 2 * value - self._lastValue
        self._lastValue = value
        return extrapoled
        # self.fifo.append(value)


class Hysteresis:
    def __init__(self, hysteresis=0.5):
        self.hysteresis = hysteresis
        self._lastValue = None
        self._sens = 1

    def inValue(self, value):
        if self._lastValue is None:
            self._lastValue = value
            return value
        if self._sens == 1:  # on est en train de monter
            if value > self._lastValue:
                self._lastValue = value
                return value
            elif value < self._lastValue - self.hysteresis:
                self._lastValue = value
                self._sens = -1
                return value
            else:
                return self._lastValue
        else:  # on est en train de descendre
            if value > self._lastValue + self.hysteresis:
                self._lastValue = value
                self._sens = 1
                return value
            elif value < self._lastValue:
                self._lastValue = value
                return value
            else:
                return self._lastValue


class HysteresisWithoutJump:
    def __init__(self, hysteresis=0.5, minimum=None, maximum=None):
        self.hysteresis = hysteresis
        self.halfHysteresis = hysteresis * 0.5
        self._lastValue = None
        if minimum is not None and maximum is not None:
            self._scale = True
            self._outMin = minimum
            self._outMax = maximum
            self._inMin = minimum + self.halfHysteresis
            self._inMax = maximum - self.halfHysteresis
        else:
            self._scale = False

    def inValue(self, value):
        halfHysteresis = self.halfHysteresis
        if self._lastValue is None:
            if not self._scale:
                self._lastValue = value
            else:
                self._lastValue = numpy.clip(value, self._inMin, self._inMax)
        else:
            if value > self._lastValue + halfHysteresis:
                self._lastValue = value - halfHysteresis
            elif value < self._lastValue - halfHysteresis:
                self._lastValue = value + halfHysteresis
        if not self._scale:
            return self._lastValue
        else:
            return (
                ((self._lastValue - self._inMin) / (self._inMax - self._inMin))
                * (self._outMax - self._outMin)
            ) + self._outMin


if __name__ == "__main__":
    from qtpy import QtGui, QtWidgets, QtCore
    from SmartFramework.plot.PlotUI import PlotUI, Curve
    import numpy
    import sys

    app = QtWidgets.QApplication(sys.argv)
    plotUI = PlotUI()

    x = numpy.linspace(0.0, 4 * numpy.pi, 400)
    lenX = len(x)
    noizeLevel = 2
    noize = numpy.random.rand(lenX) * noizeLevel
    # plotUI.addCurve(Curve(x,10*numpy.cos(x)+noize))
    y1 = (5 - noizeLevel) * 0.5 * (1 - numpy.cos(x)) + noize
    hysteresis = HysteresisWithoutJump(noizeLevel, minimum=0, maximum=1)
    y2 = numpy.fromiter((hysteresis.inValue(value) for value in y1), float, lenX)
    plotUI.addCurve(Curve(x, y1, penColor=[0, 0, 200]))
    # plotUI.addCurve(Curve(x,numpy.round(y1),penColor = [0,200,0]))
    # plotUI.addCurve(Curve(x,y2,penColor = ))
    plotUI.addCurve(Curve(x, y2, penColor=[0, 255, 0]))
    plotUI.addCurve(Curve(x, numpy.round(y2), penColor=[250, 0, 0]))
    plotUI.resize(QtCore.QSize(1000, 500))
    plotUI.show()

    app.exec_()  # pas besoin si on n'utilise pas de signaux
