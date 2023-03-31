from qtpy import QtCore, QtGui, QtWidgets

# from SmartFramework.events.time import *
# from SmartFramework.events.evt import Evt
from time import perf_counter


class ThreadSequencer(QtCore.QObject):

    getInputs = QtCore.Signal()
    analyse = QtCore.Signal()
    # time    = QtCore.Signal((float,),(int,),(int,float,),)

    def __init__(
        self,
        parent=None,
        interval=1,
        singleShot=False,
        autoStart=True,
        emitOnStart=True,
    ):
        super(ThreadSequencer, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(interval)
        self.evts = []
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.process)
        self.processing = False
        self.virtualTime = perf_counter()
        if autoStart:
            QtCore.QTimer.singleShot(0, self.start)

    def getTime(self):
        if not self.processing:
            return perf_counter()
        else:
            return self.virtualTime

    def getVirtualTime(self):
        return self.virtualTime

    def recEvt(self, evt):
        self.evts.append(evt)
        self.evts.sort()
        # print(self.evts)

    def process(self):
        # self.analyse.emit()
        timeclock = perf_counter()

        self.getInputs.emit()
        self.processing = True
        while len(self.evts) > 0 and timeclock >= self.evts[0][0]:
            evt = self.evts.pop(0)
            if evt[0] < self.virtualTime:
                print("retour en arriere dans temps virtuel")
            self.virtualTime = evt[0]
            if len(evt) > 2:
                evt[1](evt[2])
            else:
                evt[1]()
            # timeclock = perf_counter()
        self.virtualTime = timeclock
        self.processing = False

    @QtCore.Slot()
    def start(self):
        self.timer.start()

    @QtCore.Slot()
    def stop(self):
        self.timer.stop()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ThreadSequencer()
    try:
        widget.show()
    except:
        pass
    sys.exit(app.exec_())