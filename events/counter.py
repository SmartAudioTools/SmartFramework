from qtpy import QtCore, QtWidgets


class Counter(QtCore.QObject):
    output = QtCore.Signal((object,), (int,), (float,))
    finished = QtCore.Signal()

    def __init__(
        self, parent=None, cyclique=True, minValue=0, maxValue=1000, incStep=1
    ):
        super(Counter, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.cyclique = cyclique
        self.minValue = minValue
        self.maxValue = maxValue
        self.incStep = incStep
        self.value = minValue

    @QtCore.Slot()
    def inc(self):
        newValue = self.value + self.incStep
        if newValue > self.maxValue:
            if self.cyclique:
                self.value = self.minValue
                self.outValue()
            self.finished.emit()

        else:
            self.value = newValue
            self.outValue()

    @QtCore.Slot()
    def reset(self):
        self.value = self.minValue

    def outValue(self):
        obj = self.value
        typeObj = type(obj)
        if typeObj == int:
            self.output[int].emit(obj)
        elif typeObj == float:
            self.output[float].emit(obj)
        self.output[object].emit(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Counter()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())