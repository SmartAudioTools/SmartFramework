# -*- coding: utf-8 -*-
from qtpy import QtCore, QtGui, QtWidgets


class ControlMapper(QtCore.QObject):

    # Constructor

    def __init__(
        self,
        parent=None,
        inMin=0.0,
        inMax=1.0,
        outMin=0.0,
        outMax=1.0,
        curve=1.0,
        revert=False,
        hysteresis=0.04,
        median=3,
        medianTrue=False,
        trigger=False,
    ):
        super(ControlMapper, self).__init__(parent)
        # self.__dict__.update(locals()) # suprimé pour éviter reférence circulaire lors de la sérialisation
        self.inMin = inMin
        self.inMax = inMax
        self.outMin = outMin
        self.outMax = outMax
        self.curve = curve
        self.revert = revert
        self.hysteresis = hysteresis
        self.median = median
        self.medianTrue = medianTrue
        self.trigger = trigger

        self._learn = False
        self._lastOutValue = None
        self._lastOutValueInt = None
        self._lastInValues = []
        self._lastValue = 0
        self._sens = 1

    # signals

    outControl = QtCore.Signal((float,), (int,))
    outControlLowPriority = QtCore.Signal(int)

    # slots

    @QtCore.Slot(bool)
    def learn(self, b):
        self._learn = b
        if b:
            self._learnInMin = BIG_NUMBER
            self._learnInMax = -BIG_NUMBER
            self._learnOutMin = BIG_NUMBER
            self._learnOutMax = -BIG_NUMBER
        else:
            if self._learnInMin != BIG_NUMBER:
                self.inMin = self._learnInMin
                self.inMax = self._learnInMax
            if self._learnOutMin != BIG_NUMBER:
                self.outMin = self._learnOutMin
                self.outMax = self._learnOutMax

            # print(self.inMin)
            # print(self.inMax)
            # print(self.outMin)
            # print(self.outMax)

    @QtCore.Slot(float)
    def learnControl(self, inValue):
        if self._learn:
            self._learnOutMin = min(self._learnOutMin, inValue)
            self._learnOutMax = max(self._learnOutMax, inValue)

    @QtCore.Slot(float)
    def inControl(self, inValue):
        medianValue = self.medianValue(inValue)
        # print(inValue,medianValue)
        hysteresisValue = self.hysteresisValue(medianValue)
        if hysteresisValue:
            self.mappValue(medianValue)

    def mappValue(self, value):
        if self._learn:
            self._learnInMin = min(self._learnInMin, value)
            self._learnInMax = max(self._learnInMax, value)
        else:
            if self.trigger:
                inMean = 0.5 * (self.inMin + self.inMax)
                if value > inMean or self.revert:
                    outValue = self.outMax
                else:
                    outValue = self.outMin
            else:

                if value < self.inMin:
                    value = self.inMin
                if value > self.inMax:
                    value = self.inMax
                if self.revert:
                    outValue = (
                        (
                            ((value - self.inMin) / (self.inMax - self.inMin))
                            ** self.curve
                        )
                        * -1.0
                        * (self.outMax - self.outMin)
                    ) + self.outMax
                else:
                    outValue = (
                        (
                            ((value - self.inMin) / (self.inMax - self.inMin))
                            ** self.curve
                        )
                        * (self.outMax - self.outMin)
                    ) + self.outMin

            outValueInt = round(outValue * 127)

            if outValue != self._lastOutValue:
                self.outControl[float].emit(outValue)
                if outValueInt != self._lastOutValueInt:
                    self.outControl[int].emit(outValueInt)
                    QtCore.QTimer.singleShot(1, self.emitLowPiorityInt)
            self._lastOutValue = outValue
            self._lastOutValueInt = outValueInt

    def emitLowPiorityInt(self):
        self.outControlLowPriority.emit(self._lastOutValueInt)

    def medianValue(self, value):
        self._lastInValues.append(value)
        if self.medianTrue:
            while len(self._lastInValues) > self.median:
                del self._lastInValues[0]

            if len(self._lastInValues) == self.median:
                lastInValuesSorted = sorted(self._lastInValues)
                if self.median % 2 == 1:
                    index = (self.median - 1) / 2
                    median = lastInValuesSorted[index]

                else:
                    index2 = self.median / 2
                    index1 = index2 - 1
                    median = 0.5 * (
                        lastInValuesSorted[index1] + lastInValuesSorted[index2]
                    )

                return median
            else:
                return value
        else:
            return value

    def hysteresisValue(self, value):
        if self._sens == 1:  # on est en train de monter
            if value > self._lastValue:
                self._lastValue = value
                return value
            elif value < self._lastValue - self.hysteresis:
                self._lastValue = value
                self._sens = -1
                return value
            else:
                return None
        else:  # on est en train de descendre
            if value > self._lastValue + self.hysteresis:
                self._lastValue = value
                self._sens = 1
                return value
            elif value < self._lastValue:
                self._lastValue = value
                return value
            else:
                return None

    # properties

    @QtCore.Slot(float)
    def setCurve(self, value):
        self.__dict__["curve"] = value

    def getCurve(self):
        return self.__dict__["curve"]

    curve = QtCore.Property(float, getCurve, setCurve)

    @QtCore.Slot(bool)
    def setRevert(self, value):
        self.__dict__["revert"] = value

    def getRevert(self):
        return self.__dict__["revert"]

    revert = QtCore.Property(bool, getRevert, setRevert)

    @QtCore.Slot(float)
    def setHysteresis(self, value):
        self.__dict__["hysteresis"] = value

    def getHysteresis(self):
        return self.__dict__["hysteresis"]

    hysteresis = QtCore.Property(bool, getHysteresis, setHysteresis)

    @QtCore.Slot(int)
    def setMedian(self, value):
        self.__dict__["median"] = value

    def getMedian(self):
        return self.__dict__["median"]

    median = QtCore.Property(int, getMedian, setMedian)

    @QtCore.Slot(bool)
    def setMedianTrue(self, value):
        self.__dict__["medianTrue"] = value

    def getMedianTrue(self):
        return self.__dict__["medianTrue"]

    medianTrue = QtCore.Property(int, getMedianTrue, setMedianTrue)

    @QtCore.Slot(bool)
    def setTrigger(self, value):
        self.__dict__["trigger"] = value

    def getTrigger(self):
        return self.__dict__["trigger"]

    trigger = QtCore.Property(int, getTrigger, setTrigger)


BIG_NUMBER = 99999
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = ControlMapper()
    app.exec_()