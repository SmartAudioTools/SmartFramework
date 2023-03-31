from qtpy import QtGui, QtCore, QtWidgets
import sys, os
import numpy
from PlotUI import PlotUI, Curve, Pen

# from PlotWithCurveSelectorUnblockingUI import PlotWithCurveSelectorUnblockingUI
from PlotWithCurveSelectorUI import PlotWithCurveSelectorUI

# Datas

xInt = numpy.arange(30)
xFloat = numpy.linspace(0, 30, 100)
square = numpy.full_like(xInt, 35)
square[0:5] = 0
square[10:15] = 0
square[20:25] = 0
rampe = xInt - 20
hanningWithNaN = numpy.hanning(100) * 50 - 20
hanningWithNaN[7:10] = numpy.NaN
hanningWithNaN[11:13] = numpy.NaN
names = ["martin", "baptiste", "remi", "helene", "pierre", "minique"]
richesse = [15, 1, 20, 15, 35, 30]
reproduction = [0, 0, 4, 3, 4, 4]

# Plotting

app = QtWidgets.QApplication(sys.argv)
# plotUI = PlotWithCurveSelectorUnblockingUI()
plotUI = PlotWithCurveSelectorUI()

plotUI.addCurve(
    Curve(
        xFloat,
        hanningWithNaN,
        name="hanning avec NaN",
        pen=Pen([255, 0, 255]),
        visibleByDefault=True,
    )
)
# plotUI.addCurve(Curve(None,rampe+15,name = "rampe2",pen = Pen([0,0,255],QtCore.Qt.DashLine),visibleByDefault = True))
plotUI.addCurve(
    Curve(xInt, square, name="square", pen=Pen([255, 150, 0]), visibleByDefault=True)
)
plotUI.addCurve(
    Curve(
        names,
        richesse,
        name=["trucs de la vie", "richesse"],
        pen=Pen([0, 255, 0], 2.0),
        visibleByDefault=True,
    )
)
plotUI.addCurve(
    Curve(
        names,
        reproduction,
        name=["trucs de la vie", "taux reproduction"],
        pen=Pen([0, 255, 0], 2.0),
        visibleByDefault=True,
    )
)
# plotUI.setXCursor(10)
plotUI.resize(QtCore.QSize(2000, 600))
plotUI.show()  #
# app.processEvents()
# app.exec_() # pas besoin si on n'utilise pas de signaux
