# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets


class FloatSliderUI(QtWidgets.QSlider):

    valueChangedFloat = QtCore.Signal(float)

    def __init__(
        self,
        parent=None,
        minimum=0.0,
        maximum=1.0,
        value=0.0,
        orientation=QtCore.Qt.Horizontal,
        **kwargs
    ):
        QtWidgets.QSlider.__init__(
            self, parent, orientation=orientation, maximum=10000.0, **kwargs
        )
        self._value = value
        self._maximum = maximum
        self._minimum = minimum
        if value != minimum:
            self.updateSliderPosition()
        self.valueChanged.connect(self.emitFloatValue)

    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setMaximum(self, maximum):
        self._maximum = maximum
        if self._value > maximum:
            self._value = maximum

    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setMinimum(self, minimum):
        self._minimum = minimum
        if self._value < minimum:
            self._value = minimum

    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setValue(self, value):
        if value < self._minimum:
            self._value = self._minimum
        elif value > self._maximum:
            self._value = self._maximum
        else:
            self._value = value
        self.updateSliderPosition()

    def updateSliderPosition(self):
        sliderPosition = (
            (self._value - self._minimum) * 10000.0 / (self._maximum - self._minimum)
        )
        QtWidgets.QSlider.setValue(self, sliderPosition)

    def emitFloatValue(self, sliderIntValue):
        self._value = (
            self.value() * (self._maximum - self._minimum) / 10000.0 + self._minimum
        )
        self.valueChangedFloat.emit(self._value)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = FloatSliderUI()
    widget.show()
    app.exec_()
