from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.events.threadSequencer import ThreadSequencer

# from SmartFramework.events.time import *


class Timer(QtCore.QObject):
    output = QtCore.Signal()

    def __init__(self, parent=None, interval=1, autoStart=True, emitOnStart=True):
        super(Timer, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.interval = interval * 0.001
        self.emitOnStart = emitOnStart
        thread = self.thread()
        if not hasattr(thread, "threadSequencer"):
            thread.threadSequencer = ThreadSequencer(thread)
        if autoStart:
            QtCore.QTimer.singleShot(0, self.start)

    @QtCore.Slot()
    @QtCore.Slot(int)
    def start(self, interval=None):
        if interval != None:
            self.interval = interval * 0.001
        if self.emitOnStart:
            self.outputTick()
        self.nextTime = self.interval + self.thread().threadSequencer.getTime()
        self.nextEvent = (self.nextTime, self.receiveEvt)
        self.thread().threadSequencer.recEvt(self.nextEvent)

    def receiveEvt(self):
        self.nextTime = self.interval + self.nextTime
        self.nextEvent = (self.nextTime, self.receiveEvt)
        self.thread().threadSequencer.recEvt(self.nextEvent)
        self.outputTick()

    @QtCore.Slot(int)
    def setInverval(self, interval):
        self.interval = interval * 0.001

    @QtCore.Slot()
    def stop(self):
        self.thread().threadSequencer.evts.remove(self.nextEvent)

    def outputTick(self):
        # print('timeout')
        self.output.emit()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = Timer(interval=1)
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())
