from SmartFramework.plot.PlotUI import Curve, Pen
from SmartFramework.plot.PlotWithCurveSelectorUI import PlotWithCurveSelectorUI
from SmartFramework.plot.ColorEnumerator import ColorEnumerator
from SmartFramework.files import (
    joinPath,
    directory,
    removeExistingPathAndCreateFolder,
    searchExt,
    name,
)
from SmartFramework.serialize import serializejson
from qtpy import QtWidgets
import sys

visible_serializerName = {
    "pickle",
    "serializejson_no_compression",
    "serializejson_no_compression_in_file",
}
app = QtWidgets.QApplication(sys.argv)
plotUI = PlotWithCurveSelectorUI(antialising=True, rotation=90)
colorEnumerator = ColorEnumerator()
jsonPaths = searchExt(directory(__file__) + "/serialized/", "json")
for jsonPath in jsonPaths:
    print(name(jsonPath))
    dumps_or_loads_times_by_type = serializejson.load(jsonPath)
    for dumps_or_loads, times_by_type in dumps_or_loads_times_by_type.items():
        for serializerName in reversed(list(times_by_type.keys())):
            color = colorEnumerator.getNewColor()
            varnames, loads_times = zip(*times_by_type[serializerName].items())
            visibleByDefault = serializerName in visible_serializerName
            curve = Curve(
                list(varnames),
                list(loads_times),
                [name(jsonPath), dumps_or_loads, serializerName],
                Pen(color),
                visibleByDefault=visibleByDefault,
            )
            plotUI.addCurve(curve)

plotUI.show()
app.exec_()  # pas besoin si on n'utilise pas de signaux
