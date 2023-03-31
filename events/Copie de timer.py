from qtpy import QtCore, QtGui, QtWidgets


class Timer(QtCore.QObject):

    output = QtCore.Signal()

    def __init__(self, parent=None, interval=1, singleShot=False, autoStart=True):
        super(Timer, self).__init__(parent)
        self.__dict__.update(locals())
        self.timer = QtCore.QTimer()
        self.timer.setInterval = interval
        self.timer.setSingleShot = singleShot
        # self.timer.timeout.connnect()
        # QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.output)
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
    def stop(self, in2):
        self.timer.stop()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Timer()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
