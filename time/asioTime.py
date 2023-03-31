FIREWIRE_PERIODE = 0.000125
# seuil sur le residu de l'interval % 125 msec qui permet de selectionner les points qui seront utilisé pour fiting:
SEUIL_DEVIATION = 0.00001
ASIO_VS_FIREWIRE_DRIFT_MAX_DEVIATION = 0.1

from SmartFramework.stats.lastSquare import *
from SmartFramework.stats.quantificationModel import *


class AsioTime(object):
    def __init__(
        self,
        sampleRate,
        blockSize,
        asioVsFireWireDrift=1.0,
        fireWireVsClockDrift=1.0,
        fireWirePeriode=FIREWIRE_PERIODE,
        asioVsFireWireDriftMaxDeviation=ASIO_VS_FIREWIRE_DRIFT_MAX_DEVIATION,
        debug=False,
    ):

        # constantes -------
        self.sampleRate = sampleRate
        self.invSampleRate = 1.0 / sampleRate
        self.blockSize = blockSize
        self.invBlockSize = 1.0 / blockSize
        self.asioPeriode = blockSize / (sampleRate * 1.0)
        self.invAsioPeriode = (sampleRate * 1.0) / blockSize
        self.fireWirePeriode = fireWirePeriode

        # defini un a et b par defaut (pour permetre d'utiliser unifieTime sans avoir calibré Asio) ----
        self.a = self.asioPeriode
        self.b = 0.0

        # interne -----------------------------------------------
        # modelisations ------------
        self.fireWirecVsClock = LastSquareRecursiveExpReweightLiars(
            a=FIREWIRE_PERIODE, T=1000, seuil=0.00002, debug=debug
        )  # si baisse trop le seuil il decroche avec PyAudio sur CPU 1 en priorité normale
        aAsioVsFireWireTheorique = blockSize / (sampleRate * fireWirePeriode)
        self.asioVsFireWire = QuantificationModelFiltreAndLastSquare(
            aAsioVsFireWireTheorique,
            asioVsFireWireDrift,
            asioVsFireWireDriftMaxDeviation,
            debug=debug,
        )

        # variables internes ------
        self._na = -1
        self._nf = 0
        self._lastValidTime = None
        self._lastTime = 0.0

        # debug ------
        self.debug = debug
        if debug:
            self.points = []  # listes pour debugage

    # lecture ---------------------------------------------------------------------------------
    def getAsioTime(self):
        t = clock
        return self.asioPeriode * (t - self.b) / self.a

    # conversions asioTime <-> asio sample <-> asio block,sample <-> asio bloc ----------------
    def timeToSample(self, t):
        return t * self.sampleRate

    def sampleToTime(self, s):
        return t * self.invSampleRate

    def timeToBlock(self, t):
        """faudrait s\'assurer qeu block -> time -> block toujours invariant)"""
        return int(t * self.invAsioPeriode)

    def blockToTime(self, b):
        return b * self.asioPeriode

    def timeToBlockSample(self, t):
        s1 = t * self.sampleRate
        b = int(s1) / self.blockSize  # ou   b  = int(s1/ self.blockSize)
        s2 = s1 - b * self.blockSize
        return b, s2

    def bockSampleToTime(self, b, s):
        return b * self.blockSize + s

    def blockSampleToSample(self, b, s):
        return b * self.blockSize + s

    def sampleToBlockSample(self, s):
        b = int(s) / self.blockSize
        s2 = s - b * self.blockSize
        return b, s2

    # conversions Asio <-> Clock ---------------------------------------------------------------
    def asioTimeToClock(self, ta):
        return self.a * (ta * self.invAsioPeriode) + self.b

    def asioBlockToClock(self, na):
        return self.a * na + self.b

    def asioSampleToClock(self, sa):
        return self.a * (sa * self.invBlockSize) + self.b

    def clockToAsioTime(self, t):
        return self.asioPeriode * (t - self.b) / self.a

    # synchonisation avec perf_counter() ---------------------------------------------------------------

    def sync(self):
        t = perf_counter()
        self.newtime(t)

    def newTime(self, t):
        # incrementation du compteur de block , faudrait detectecter les overrun
        self._na += 1
        self.addpoint(self._na, t)

    def addpoint(self, na, t, wi=1.0):

        # separation de la partie quantifie du bruit ( a ameliorer)
        interval = t - self._lastTime
        self._lastTime = t
        nfDelta = round(interval / self.fireWirePeriode)
        resteInterval = interval - nfDelta * self.fireWirePeriode

        # si residu inférieur à un certain seuil => prend en compte le point
        if abs(resteInterval) < SEUIL_DEVIATION:
            # On prend en compte le dernier point
            if self._lastValidTime != None:
                interval = t - self._lastValidTime
                nfDelta = round(interval / self.fireWirePeriode)
                self._nf += nfDelta
            self.fireWirecVsClock.addPoint(self._nf, t)
            self.asioVsFireWire.addPoint(self._na, self._nf)
            self._lastValidTime = t

        # mise à jour de a et b
        self.a = self.fireWirecVsClock.a * self.asioVsFireWire.a
        self.b = (
            self.fireWirecVsClock.a * self.asioVsFireWire.b + self.fireWirecVsClock.b
        )

        # debug
        if self.debug:
            self.points.append([na, t, wi, self.a, self.b])
