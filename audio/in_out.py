from qtpy import QtCore, QtGui, uic

# a voir si on met là----------------------


class Ins(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

    def read(self):
        self.emit(QtCore.SIGNAL("audioOutput"), audioEvt)


class Outs(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

    def audioInput(self, audioEvt):
        pass


# ----------------------
class In(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        QtCore.QObject.connect(
            parent, QtCore.SIGNAL("audioOutput"), self.read, QtCore.Qt.AutoConnection
        )

    def read(self, audioEvt):
        self.emit(QtCore.SIGNAL("audioOutput"), audioEvt)


class Out(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL("audioOutput"),
            parent.writeAudio,
            QtCore.Qt.AutoConnection,
        )

    def audioInput(self, audioEvt):
        self.emit(QtCore.SIGNAL("audioOutput"), audioEvt)


class Prod(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

    def audioInput(self, audioEvt):
        self.emit(QtCore.SIGNAL("audioOutput"), audioEvt)


class Counter(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.i = 0

    def audioInput(self, audioEvt):
        self.i = (self.i + 1) % 500
        self.emit(QtCore.SIGNAL("count(int)"), self.i)


class Volume(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.vol = 0.2

    def audioInput(self, audioEvtIn):
        audioEvtOut = audioEvtIn * self.vol
        self.emit(QtCore.SIGNAL("audioOutput"), audioEvtOut)

    def setVolume(self, vol_int):
        self.vol = vol_int * 0.02


class Add(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
