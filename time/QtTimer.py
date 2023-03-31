from qtpy import QtCore, QtWidgets


class QtTimer(QtCore.QObject):

    output = QtCore.Signal()

    def __init__(self, parent=None, interval=1000, singleShot=False, autoStart=True):
        super(QtTimer, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.timer = QtCore.QTimer()
        self.setInterval(interval)
        self.setSingleShot(singleShot)
        self.timer.timeout.connect(self.output)
        self.setAutoStart(autoStart)

    @QtCore.Slot()
    @QtCore.Slot(int)
    def start(self, interval=None):
        if interval != None:
            self.timer.start(interval)
        else:
            self.timer.start()

    @QtCore.Slot()
    def stop(self):
        self.timer.stop()

    @QtCore.Slot(bool)
    def startStop(self, b):
        if b:
            self.start()
        else:
            self.stop()

    def setInterval(self, interval):
        self.timer.setInterval(interval)

    def getInterval(self):
        return self.timer.interval()

    interval = QtCore.Property(int, getInterval, setInterval)

    def setSingleShot(self, singleShot):
        self.timer.setSingleShot(singleShot)

    def getSingleShot(self):
        return self.timer.isSingleShot()

    singleShot = QtCore.Property(bool, getSingleShot, setSingleShot)

    def setAutoStart(self, autoStart):
        self._autoStart = autoStart
        if autoStart:
            QtCore.QTimer.singleShot(0, self.start)

    def getAutoStart(self):
        return self._autoStart

    autoStart = QtCore.Property(bool, getAutoStart, setAutoStart)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QtTimer()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
