# -*- coding: utf-8 -*-
from qtpy import QtCore


class MidiChannelFilter(QtCore.QObject):

    selected = QtCore.Signal(object)
    other = QtCore.Signal(object)

    def __init__(
        self,
        parent=None,
        ch00=True,
        ch01=True,
        ch02=True,
        ch03=True,
        ch04=True,
        ch05=True,
        ch06=True,
        ch07=True,
        ch08=True,
        ch09=True,
        ch10=True,
        ch11=True,
        ch12=True,
        ch13=True,
        ch14=True,
        ch15=True,
        ch16=True,
    ):
        super(MidiChannelFilter, self).__init__( parent)
        self.ch = [
            ch00,
            ch01,
            ch02,
            ch03,
            ch04,
            ch05,
            ch06,
            ch07,
            ch08,
            ch09,
            ch10,
            ch11,
            ch12,
            ch13,
            ch14,
            ch15,
            ch16,
        ]

    @QtCore.Slot(object)
    def filter(self, m):
        if self[m.getChannel()]:
            self.selected.emit(m)
        else:
            self.other.emit(m)

    def setCh00(self, value):
        self.ch[0] = value

    def getCh00(self):
        return self.ch[0]

    ch00 = QtCore.Property(bool, getCh00, setCh00)

    def setCh01(self, value):
        self.ch[1] = value

    def getCh01(self):
        return self.ch[1]

    ch01 = QtCore.Property(bool, getCh01, setCh01)

    def setCh02(self, value):
        self.ch[2] = value

    def getCh02(self):
        return self.ch[2]

    ch02 = QtCore.Property(bool, getCh02, setCh02)

    def setCh03(self, value):
        self.ch[3] = value

    def getCh03(self):
        return self.ch[3]

    ch03 = QtCore.Property(bool, getCh03, setCh03)

    def setCh04(self, value):
        self.ch[4] = value

    def getCh04(self):
        return self.ch[4]

    ch04 = QtCore.Property(bool, getCh04, setCh04)

    def setCh05(self, value):
        self.ch[5] = value

    def getCh05(self):
        return self.ch[5]

    ch05 = QtCore.Property(bool, getCh05, setCh05)

    def setCh06(self, value):
        self.ch[6] = value

    def getCh06(self):
        return self.ch[6]

    ch06 = QtCore.Property(bool, getCh06, setCh06)

    def setCh07(self, value):
        self.ch[7] = value

    def getCh07(self):
        return self.ch[7]

    ch07 = QtCore.Property(bool, getCh07, setCh07)

    def setCh08(self, value):
        self.ch[8] = value

    def getCh08(self):
        return self.ch[8]

    ch08 = QtCore.Property(bool, getCh08, setCh08)

    def setCh09(self, value):
        self.ch[9] = value

    def getCh09(self):
        return self.ch[9]

    ch09 = QtCore.Property(bool, getCh09, setCh09)

    def setCh10(self, value):
        self.ch[10] = value

    def getCh10(self):
        return self.ch[10]

    ch10 = QtCore.Property(bool, getCh10, setCh10)

    def setCh11(self, value):
        self.ch[11] = value

    def getCh11(self):
        return self.ch[11]

    ch11 = QtCore.Property(bool, getCh11, setCh11)

    def setCh12(self, value):
        self.ch[12] = value

    def getCh12(self):
        return self.ch[12]

    ch12 = QtCore.Property(bool, getCh12, setCh12)

    def setCh13(self, value):
        self.ch[13] = value

    def getCh13(self):
        return self.ch[13]

    ch13 = QtCore.Property(bool, getCh13, setCh13)

    def setCh14(self, value):
        self.ch[14] = value

    def getCh14(self):
        return self.ch[14]

    ch14 = QtCore.Property(bool, getCh14, setCh14)

    def setCh15(self, value):
        self.ch[15] = value

    def getCh15(self):
        return self.ch[15]

    ch15 = QtCore.Property(bool, getCh15, setCh15)

    def setCh16(self, value):
        self.ch[16] = value

    def getCh16(self):
        return self.ch[16]

    ch16 = QtCore.Property(bool, getCh16, setCh16)
