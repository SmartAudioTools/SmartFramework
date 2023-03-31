# -*- coding: utf-8 -*-
from qtpy import QtCore


class MidiChannelSplit(QtCore.QObject):

    ch01 = QtCore.Signal(object)
    ch02 = QtCore.Signal(object)
    ch03 = QtCore.Signal(object)
    ch04 = QtCore.Signal(object)
    ch05 = QtCore.Signal(object)
    ch06 = QtCore.Signal(object)
    ch07 = QtCore.Signal(object)
    ch08 = QtCore.Signal(object)
    ch09 = QtCore.Signal(object)
    ch10 = QtCore.Signal(object)
    ch11 = QtCore.Signal(object)
    ch12 = QtCore.Signal(object)
    ch13 = QtCore.Signal(object)
    ch14 = QtCore.Signal(object)
    ch15 = QtCore.Signal(object)
    ch16 = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(MidiChannelSplit, self).__init__(parent)
        self.ch = [
            None,
            self.ch01,
            self.ch02,
            self.ch03,
            self.ch04,
            self.ch05,
            self.ch06,
            self.ch07,
            self.ch08,
            self.ch09,
            self.ch10,
            self.ch11,
            self.ch12,
            self.ch13,
            self.ch14,
            self.ch15,
            self.ch16,
        ]

    @QtCore.Slot(object)
    def split(self, m):
        self.ch[m.getChannel()].emit(m)
