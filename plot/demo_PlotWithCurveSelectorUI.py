from qtpy import QtGui, QtCore, QtWidgets
import sys
import numpy
from SmartFramework.plot.PlotUI import Curve, Pen
from SmartFramework.plot.PlotWithCurveSelectorUI import PlotWithCurveSelectorUI

from time import perf_counter

# Datas

xInt = numpy.arange(30)
xFloat = numpy.linspace(0, 30, 100)
square = numpy.full_like(xInt, 35)
square[0:5] = 0
square[10:15] = 0
square[20:25] = 0
rampe = xInt - 10
# hanning = numpy.hanning(100)*50 - 20
hanningWithNaN = numpy.hanning(100) * 50 - 10
hanningWithNaN[7:10] = numpy.NaN
hanningWithNaN[40:55] = numpy.NaN
names = ["martin", "baptiste", "remi", "helene", "pierre", "minique"]
richesse = [15, 1, 20, 15, 35, 30]
reproduction = [0, 0, 4, 3, 4, 4]

randomCurve = Curve(
    [0.0],
    [0],
    name=["ensemble1", "random"],
    pen=Pen([100, 230, 0], 1.0),
    visibleByDefault=True,
)


wavX = numpy.linspace(10.0, 20.0, 400)
wavPhase = wavX * 3
wavHanning = numpy.hanning(400) * 20
wavCurve = Curve(
    wavX,
    numpy.sin(wavX) * wavHanning,
    name="wav",
    pen=Pen(
        [0, 0, 255],
    ),
    visibleByDefault=True,
)


# lastT = 0.
def timeout():
    t = perf_counter()
    # print(int((t-lastT)*1000))
    # lastT = t
    randomCurve.addData(
        randomCurve.X[-1] + 0.02,
        randomCurve.Y[-1] * 0.9 + (numpy.random.rand() - 0.5) * 5.0,
    )  #
    wavCurve.setData(wavX, numpy.sin(wavPhase + t) * wavHanning + 15)
    # hanningWithNaN


# Plotting

app = QtWidgets.QApplication(sys.argv)
plotUI = PlotWithCurveSelectorUI(antialising=True)
plotUI.addCurve(wavCurve)
plotUI.addCurve(randomCurve)
plotUI.addCurve(
    Curve([], [], name="empty", pen=Pen([255, 0, 255]), visibleByDefault=True)
)
plotUI.addCurve(
    Curve(None, [], name="empty2", pen=Pen([255, 0, 255]), visibleByDefault=True)
)
plotUI.addCurve(
    Curve(
        None,
        [1, 20, 23, 15, 19, 17, 20, 10, 9],
        name="y list",
        pen=Pen([255, 0, 255]),
        visibleByDefault=True,
    )
)
plotUI.addCurve(
    Curve(
        [0, 2, 3, 5, 8, 9, 11, 15, 20],
        [1, 20, 23, 15, 19, 17, 20, 10, 9],
        name="x list and y list",
        pen=Pen([255, 0, 255]),
        visibleByDefault=True,
    )
)
plotUI.addCurve(
    Curve(
        xFloat,
        hanningWithNaN,
        name="hanning avec NaN",
        pen=Pen([255, 0, 255]),
        visibleByDefault=True,
    )
)
plotUI.addCurve(
    Curve(
        None,
        rampe,
        name="rampe",
        pen=Pen([0, 0, 255], QtCore.Qt.DashLine),
        visibleByDefault=True,
    )
)
plotUI.addCurve(
    Curve(
        None,
        rampe + 10,
        name="rampe",
        pen=Pen([0, 0, 255], QtCore.Qt.DashLine),
        visibleByDefault=True,
    )
)
plotUI.addCurve(
    Curve(
        xInt,
        square,
        name=["ensemble1", "square"],
        pen=Pen([255, 150, 0]),
        visibleByDefault=True,
    )
)
# plotUI.addCurve(Curve(names,richesse,name = ["trucs de la vie","richesse"],pen = Pen([0,255,0],2.),visibleByDefault = True))
# plotUI.addCurve(Curve(names,reproduction,name = ["trucs de la vie","taux reproduction"],pen = Pen([0,255,0],2.),visibleByDefault = True))
plotUI.setXCursor(10)
plotUI.resize(QtCore.QSize(2000, 600))
plotUI.show()

timer = QtCore.QTimer()
timer.setInterval(20)
timer.timeout.connect(timeout)
timer.start()


app.exec_()  # pas besoin si on n'utilise pas de signaux
timer.stop()
print("finished")
