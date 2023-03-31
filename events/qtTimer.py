from qtpy import QtCore, QtGui, QtWidgets


class QtTimer(QtCore.QObject):

    output = QtCore.Signal()

    def __init__(self, parent=None, interval=1000, singleShot=False, autoStart=True):
        super(QtTimer, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.timer = QtCore.QTimer()
        self.timer.setInterval(interval)
        self.timer.setSingleShot(singleShot)

        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.outputTick)
        if autoStart:
            QtCore.QTimer.singleShot(0, self.start)

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

    def outputTick(self):
        self.output.emit()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QtTimer()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
