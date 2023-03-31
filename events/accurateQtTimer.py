from qtpy import QtCore, QtGui, QtWidgets


class AccurateQtTimer(QtCore.QObject):

    output = QtCore.Signal()

    def __init__(
        self,
        parent=None,
        interval=1000,
        singleShot=False,
        autoStart=False,
        emitOnStart=True,
    ):
        super(AccurateQtTimer, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.interval = interval
        self.singleShot = singleShot
        self.autoStart = autoStart
        self.emitOnStart = emitOnStart
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1)
        # self.timer.setSingleShot(singleShot)

        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.count)
        if autoStart:
            QtCore.QTimer.singleShot(0, self.start)

    def count(self):
        self.msec += 1
        # print(self.msec)
        while self.msec >= self.nextTick:
            # print('self.nextTick:' + str(self.nextTick ))
            self.nextTick = (
                self.nextTick + self.interval
            )  # integre une erreure , mais permet modification dynamique de l'inteval
            # print('output')
            self.outputTick()
        # print(self.msec)

    @QtCore.Slot()
    @QtCore.Slot(int)
    def start(self, interval=None):
        if interval != None:
            self.interval = interval
        if self.emitOnStart:
            # print('emitonstart')
            self.outputTick()
        self.msec = 0
        self.nextTick = self.interval
        self.timer.start()

    @QtCore.Slot(int)
    def setInverval(self, interval):
        self.interval = interval

    @QtCore.Slot()
    def stop(self):
        self.timer.stop()

    def outputTick(self):
        # print('output')
        self.output.emit()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = AccurateQtTimer(interval=1000)
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
