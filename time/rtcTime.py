from SmartFramework.stats.lastSquare import LastSquareRecursiveExpReweightLiars
from windowsTime import timeGetTime, timeBeginPeriod, FileTimeAtStartUp, utcFromFileTime
from fixed import fixedFromFloat
from math import ceil
from time import perf_counter

FREQ_RTC = 1024


class RtcTime(object):
    def __init__(self, debug=False):
        # stock constantes
        self.rtcPeriode = 1.0 / FREQ_RTC
        self.rtcFreq = FREQ_RTC

        # stock données pour debugage
        self.debug = debug
        if debug:
            self.points = []  # listes pour debugage

        # force timeBeginPeriod(1)
        timeBeginPeriod(1)

        # calcul offsets
        self.findOffset()  # cherhe l'offset de timeGetTime() avant troncature
        offsetArrondiGetTickCount = (
            ceil(self.offset * self.rtcFreq) * self.rtcPeriode - self.offset
        )
        offsetTimeBeginPeriod = -15.5 * self.rtcPeriode
        self.offsetUrtc = utcFromFileTime(FileTimeAtStartUp) + fixedFromFloat(
            offsetTimeBeginPeriod + offsetArrondiGetTickCount
        )

        # Rtc vs perf_counter() : intialise et première mesures
        self.nRtcVsClock = LastSquareRecursiveExpReweightLiars(
            a=self.rtcPeriode, T=1000, seuil=1.0, debug=debug
        )
        self.activSync(1000)

    # lecture RTC & URTC -----------

    def getUrtc(self):
        """retourne le temps continu de la RTC depuis 1 janvier 1970 au format "fixed" (64 bits , virgules fixe sur 32 ème bit)"""
        t = perf_counter()
        return self.rtcToUrtc(self.clockToRtc(t))

    def getRtc(self):
        """retourne le temps continu de la RTC depuis creation de l'objet RtcTime() soit importation de la bibliotheque ?"""
        t = perf_counter()
        return self.clockToRtc(t)

    def getDiscretRtc(self):
        """retourne le temps discret du dernier tick de RTC (avec trous car utilise timeGetTime)
        depuis creation de l'objet RtcTime() soit importation de la bibliotheque ?"""
        tgt = timeGetTime()
        return self.timeGetTimeToRtc(tgt)

    # conversions % RTC -----

    def rtcToClock(self, tRtc):
        return (
            self.nRtcVsClock.a * (tRtc - self.offset) * self.rtcFreq
            + self.nRtcVsClock.b
        )

    def clockToRtc(self, t):
        return (
            (t - self.nRtcVsClock.b) / self.nRtcVsClock.a
        ) * self.rtcPeriode + self.offset

    def timeGetTimeToRtc(self, tgt):
        return (
            ceil((tgt - self.offsetMsec) * self.rtcFreq * 0.001) * self.rtcPeriode
            + self.offset
        )

    def rtcToTimeGetTime(self, rtc):
        return int(rtc * 1000.0)

    def rtcToUrtc(self, rtc):
        """a verifier"""
        return int(rtc * (2**32)) + self.offsetUrtc

    def urtcToRtc(self, urtc):
        """a verifier"""
        return (urtc - self.offsetUrtc) * (2**-32)

    # ajout de donnée de synchronisation Rtc/clock---------

    def activSync(self, N=1):
        """synchronisation par ajoute de N points , par sondage actif de changement de timeGetTime()"""
        time = timeGetTime()
        for i in range(N):
            while time == timeGetTime():
                pass
            c = perf_counter()
            time = timeGetTime()
            self.addPoint(time, c)

    def sync(self):
        """synchronisation sur interuption d'un timer multimedia"""
        t = perf_counter()
        tgt = timeGetTime()
        self.addPoint(tgt, t)

    def newTime(self, t):
        """synchronisation par ajout du perf_counter() mesurée sur dernière interuption d'un timer multimedia"""
        tgt = timeGetTime()
        self.addPoint(tgt, t)

    def addPoint(self, tgt, t, wi=1.0):
        """synchronisation par ajout d'un point (timeGetTime(), perf_counter(), weight))
        pour l'instant fait moindre carré sur compteur nRtc entier, à partir du lancement de l'application ,
        permet d'avoir des calculs plus précis...
        """
        n = ceil((tgt - self.offsetMsec) * (self.rtcFreq * 0.001))
        self.nRtcVsClock.addPoint(n, t)

    # properties ---------

    @property
    def a(self):
        return self.nRtcVsClock.a * self.rtcFreq

    @property
    def b(self):
        return self.nRtcVsClock.b - self.offset * self.nRtcVsClock.a * self.rtcFreq

    # Interne ----------

    def findOffset(self):

        # cherche l'offset

        nb_max_test = 1000
        nb_test = 0
        oldTimeGetTime = -1
        while nb_test < nb_max_test:
            nb_test += 1
            while 1:
                newTimeGetTime = timeGetTime()
                if newTimeGetTime != oldTimeGetTime:
                    if newTimeGetTime - oldTimeGetTime == 1:
                        c = perf_counter()
                        listClock.append(c)
                        listTimeGetTime.append(newTimeGetTime)
                        i += 1
                        break
                    else:
                        # on a loupé une interuption du timerMultimedia ...
                        listTimeGetTime = []
                        listClock = []
                        oldTimeGetTime = timeGetTime()
                        i = -1

            oldTimeGetTime = newTimeGetTime

            if i >= 42 and ((listClock[(i - 41)] - listClock[i - 42]) > 0.0015) & (
                (listClock[i] - listClock[i - 1]) > 0.0015
            ):
                indexOffset = i - 42
                self.offsetMsec = listTimeGetTime[indexOffset]
                self.offset = self.offsetMsec * 0.001
                break
        else:
            raise Exception(
                "impossible de trouver offset du timer Multimedia , essayez de desactiver les drivers wifi,ethernet,et de tuer les processus pouvant poser probleme"
            )
        del listClock
        del listTimeGetTime

    # print(self.offsetMsec)


if __name__ == "__main__":
    import gc

    gc.disable()

    rtcTime = RtcTime(debug=True)

    import numpy as np
    import matplotlib.pyplot as plt

    nRtcVsClockArray = np.array(rtcTime.nRtcVsClock.points)

    X = nRtcVsClockArray[:, 0]
    Y = nRtcVsClockArray[:, 1]
    W = nRtcVsClockArray[:, 2]
    A = nRtcVsClockArray[:, 3]
    B = nRtcVsClockArray[:, 4]
    Ymodelised = nRtcVsClockArray[:, 5]
    # Ymodelised2 = A * X + B  # donne exactement le meme resultat

    moindreCarreRtcVsClockAXY = np.polyfit(X, Y, 1)
    Yresidu = Y - np.polyval(moindreCarreRtcVsClockAXY, X)
    plt.plot(X, Yresidu * 1000000.0, ",")

    YmodelisedResidu = Ymodelised - np.polyval(moindreCarreRtcVsClockAXY, X)
    plt.plot(X, YmodelisedResidu * 1000000.0, "r")

    plt.title(
        "RTC tick counter * RTC frequency Vs QueryPerformanceCounter (Mesured vs Modelised )residue in us"
    )

    plt.show()
