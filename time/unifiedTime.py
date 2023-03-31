# -*- coding: utf-8 -*-
from SmartFramework.time import asioTime, rtcTime, ntpTime
from time import perf_counter

FREQ_RTC = 1024


class UnifiedTime(object):
    """
    pour l'instant se cale sur l'asioTime
    tant que l'asio n'est pas qualibré , l'asioTime est callé sur perf_counter()
    ( asioTime.a = asioPeriode  et     asioTime.b = 0.)
    dans l'idéal faudrait se caller plutot sur Rtc
    un fois la calibration asio effectué , il faut re-computeOffsetUtc()
    """

    def __init__(self, debug=False):
        self.rtcTime = rtcTime.RtcTime()
        self.asiotTime = asioTime.AsioTime(44100, 96)
        self.computeOffsetUtc()  # dans l'idéal il faudrait recalculer l'offset aprés

    # lecture Time & UTC -----------

    def getTime(self):
        """Time (temps depuis demarage de l'horloge de reference)"""
        c = perf_counter()
        return self.asiotTime.clockToAsioTime(c)

    def getUtc(self):
        """UTC (date de réference definie dans fixed.py , en l'occurence pour l'instant 1er janvier 1900)"""
        c = perf_counter()
        tAsio = self.asiotTime.clockToAsioTime(c)
        return int(tAsio * (2**32)) + self.offsetUtc

    # conversions  -------------------

    #  time <-> UTC

    def timeToUtc(self, t):
        return int(t * (2**32)) + self.offsetUtc

    def utcToTime(self, u):
        return int(t * (2**32)) + self.offsetUtc

    # time <-> Asio

    def asioToTime(self, tAsio):
        return tAsio

    def timeToAsio(self, t):
        return t

    # time <-> clock

    def clockToTime(self, c):
        return self.asiotTime.clockToAsioTime(c)

    def timeToClock(self, t):
        return self.asiotTime.asioTimeToClock(t)

    # time <-> rtc

    def rtcToTime(self, r):
        return self.clokToTime(self.rtcTime.rtcToClock(r))

    def timeToRtc(self, t):
        return self.rtcTime.clockToRtc(self.timeToClock(t))

    # time <-> timeGetTime

    def timeGetTimeToTime(self, tgt):
        return self.clockToTime(self.rtcTime.rtcToClock(self.timeGetTimeToRtc(tgt)))

    def timeToTimeGetTime(self, t):
        return self.rtcTime.rtcToTimeGetTime(
            self.rtcTime.clockToRtc(self.timeToClock(t))
        )

    # internet ----------------------
    def computeOffsetUtc(self):
        """petite aproximation : on supose que les drifts de la perf_counter() est négliable
        soit que self.rtcTime.nRtcVsClock.a ~= periodeRTC
        entre mesure de l'offset Asio et mesure de l'offset de la RTC
         cf Demo
        """
        self.offsetUtc = (
            int((self.asiotTime.b - self.rtcTime.nRtcVsClock.b) * (2**32))
            + self.rtcTime.offsetUrtc
            + int(self.rtcTime.offset * (2**32))
        )


if __name__ == "__main__":

    unifiedTime = UnifiedTime()
