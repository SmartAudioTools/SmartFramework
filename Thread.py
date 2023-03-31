from qtpy import QtCore


class Thread(QtCore.QThread):
    def __init__(self, parent=None, priority=6, **kargs):
        self._priority = priority  #
        if isinstance(self, QtCore.QThread):
            QtCore.QThread.__init__(self, parent, **kargs)
            self.start()
        else:
            QtCore.QObject.__init__(self, parent, **kargs)

    def setPriority(self, priority):
        self._priority = priority

    def getPriority(self):
        return self._priority

    priority = QtCore.Property(int, getPriority, setPriority)

    def start(self):
        print("start thread")
        QtCore.QThread.start(self, priority=self._priority)

    # def run(self):
    #    while True:
    #        pass
    #    self.exec()
