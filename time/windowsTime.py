# -*- coding: utf-8 -*-
""" module wrappant les fonctions windows, plus quelques fonction de conversion """

# from struct import pack, unpack
from ctypes import windll, Structure, c_ushort, c_ulong, c_long, c_int64, byref
from math import ceil
from time import perf_counter
from .timeParameters import NTP_EPOCH, WINDOWS_EPOCH

kernel32_GetSystemTime = windll.kernel32.GetSystemTime
kernel32_SetSystemTime = windll.kernel32.SetSystemTime
kernel32_GetSystemTimeAsFileTime = windll.kernel32.GetSystemTimeAsFileTime
kernel32_GetSystemTimeAdjustment = windll.kernel32.GetSystemTimeAdjustment
kernel32_SetSystemTimeAdjustment = windll.kernel32.SetSystemTimeAdjustment
kernel32_SystemTimeToFileTime = windll.kernel32.SystemTimeToFileTime
kernel32_FileTimeToSystemTime = windll.kernel32.FileTimeToSystemTime
kernel32_GetTickCount = windll.kernel32.GetTickCount
kernel32_QueryPerformanceCounter = windll.Kernel32.QueryPerformanceCounter
kernel32_QueryPerformanceFrequency = windll.Kernel32.QueryPerformanceFrequency


# comparaison à UTC de reference
NTP_WINDOWS_DELTA = (NTP_EPOCH - WINDOWS_EPOCH).days * 24 * 3600 * 2**32


# conversions -----------


def utcFromFileTime(ft):
    """convertit FileTime -> UTC.
    Attention : en C on aurait un dépassement"""
    return int((ft << 32) / 10000000) + NTP_WINDOWS_DELTA


def fileTimeFromUtc(utc):
    """convertit UTC->FiteTime .
    Attention : en C on aurait un dépassement"""
    return ((utc - NTP_WINDOWS_DELTA) * 10000000) >> 32


# structures -----------------------


class SYSTEMTIME(Structure):
    _fields_ = (
        ("wYear", c_ushort),
        ("wMonth", c_ushort),
        ("wDayOfWeek", c_ushort),
        ("wDay", c_ushort),
        ("wHour", c_ushort),
        ("wMinute", c_ushort),
        ("wSecond", c_ushort),
        ("wMilliseconds", c_ushort),
    )

    def __str__(self):
        return "%4d%02d%02d%02d%02d%02d.%03d" % (
            self.wYear,
            self.wMonth,
            self.wDay,
            self.wHour,
            self.wMinute,
            self.wSecond,
            self.wMilliseconds,
        )


class LONG_INTEGER(Structure):
    _fields_ = (
        ("low", c_ulong),
        ("high", c_long),
    )


# CPU time --------------------------


def QPC():
    """appel kernel32_QueryPerformanceCounter ,plus couteux qu\'un perf_counter(), et pas meme reference"""
    v = c_int64()
    kernel32_QueryPerformanceCounter(byref(v))
    return v.value


def QPF():
    """kernel32_QueryPerformanceFrequency(byref(v))"""
    v = c_int64()
    kernel32_QueryPerformanceFrequency(byref(v))
    return v.value


def QPCToClock(i):
    return (i + init_qpc) * inv_qpf


def ClockToQPC(t):
    return int(t * qpf) - init_qpc


# interne ---


def initQPCconv():
    qpf = 1.0 * QPF()
    inv_qpf = 1.0 / QPF()
    c1 = 0.0
    c2 = 1.0
    i = 0
    while c2 - c1 > 1e-05 and i < 1000:
        c1 = perf_counter()
        qpc = QPC()
        c2 = perf_counter()
    c = (c1 + c2) / 2.0
    init_qpc = (
        int(c * qpf) - qpc
    )  # avance en nombre de Qpc de perf_counter() sur QueryPerformanceCounter.
    return qpf, inv_qpf, init_qpc


qpf, inv_qpf, init_qpc = initQPCconv()

# inutile ---


def modQPC():
    """modelise appel de kernel32_QueryPerformanceCounter en faisant en vrais appel à perf_counter() .coute autant que QPC() => sert à rien"""
    return int(perf_counter() * qpf) - init_qpc


# Multimedia time --------------------------

timeGetTime = windll.winmm.timeGetTime  # retourne temps en msec (cf timeGetTime)
timeEndPeriod = (
    windll.winmm.timeEndPeriod
)  # suprime dernier  times periode de 1msec '''


def timeBeginPeriod(period):
    """fixe la timeBeginPeriode, en bloquant tant qu\'elle n'est pas réelement effective"""
    global nbTimeBegin
    nbTimeBegin = nbTimeBegin + 1
    windll.winmm.timeBeginPeriod(period)

    oldTime = timeGetTime()
    newTime = oldTime
    while (newTime - oldTime) != period:
        oldTime = newTime
        newTime = timeGetTime()


def removeTimePeriod():
    """suprime recursivement les times periode de 1msec"""
    while 0 == timeEndPeriod(1):
        pass


# inutile ---

nbTimeBegin = 0


def getNbTimeBegin():
    return nbTimeBegin


def getTimePeriod():
    from time import sleep

    t1 = timeGetTime()
    sleep(0.001)
    t2 = timeGetTime()
    return t2 - t1 - 1


# system et windows time WRAPERS -------------------------


def GetTickCount():
    """nombre de millisecondes  (a 15 msec prés)  qui se sont écoulés depuis le démarrage du système.
    en réalité  :
    somme des incrementations de 15.625 msec   (toujours , meme si appele synchro NTP ou manuelle )
    effectuées (depuis demargage) sur les interuption systeme qui on lieu toute les 15.625 msec
    (PIT (ou du HPET) branchée sur IRQ 0 si timeBeginPeriod(15) (par defaut)
    ou  toutes les 16 interuptions de la RTC  RTC (ou du HPET)  branchée sur IRQ 8 si timeBeginPeriod(1)
    => petit cafouillage autour de timeBeginPerdiode(1))
    tronqué dans un un entier 32 bits correspondant à des mili-secondes
    + n'est pas affecté par les ajustements apportés par la fonction GetSystemTimeAdjustment
    + Le temps écoulé récupérées par GetTickCount ou GetTickCount64 inclut le temps le système passé en veille ou d'hibernation => donc doit recuperer infos de la RTC...."""
    return windll.kernel32.GetTickCount()


def GetAccurateTickCount(Tc):
    """version exacte (sans trancature) de GetTickCount:"""
    return ceil(GetTickCount() / 15.625) * 15.625


def GetSystemTime():
    """nombre de millisecondes (a 15 msec prés)  qui se sont écoulés depuis 1er janvier 1601.
    retourne GetSystemTimeAsFileTime()  tronqué  à la msec dans une structure SYSTEMTIME.
    Utilisez plutot GetSystemTimeAsFileTime()"""
    st = SYSTEMTIME(0, 0, 0, 0, 0, 0, 0, 0)
    ft = LONG_INTEGER(0, 0)
    kernel32_GetSystemTime(byref(st))
    kernel32_SystemTimeToFileTime(byref(st), byref(ft))
    # print("ft.high:",str(ft.high),"ft.low:",str(ft.low))
    return int(((int(ft.high) << 32) | ft.low) * 0.0001)


def SetSystemTime(msecSince1601):
    ft = LONG_INTEGER(0, 0)
    st = SYSTEMTIME(0, 0, 0, 0, 0, 0, 0, 0)
    fileTime = 10000 * msecSince1601
    ft.high = fileTime >> 32
    ft.low = fileTime - (ft.high << 32)
    # print("ft.high:",str(ft.high),"ft.low:",str(ft.low))
    kernel32_FileTimeToSystemTime(byref(ft), byref(st))
    return kernel32_SetSystemTime(byref(st))


def GetSystemTimeAsFileTime():
    """nombre entier de 100 nano-secondes (a 15 msec prés)  qui se sont écoulés depuis 1er janvier 1601.
    en réalité  :
    retourne  l'heure de la RTC au demarage  (depuis 1er janvier 1601 )
    + somme des incrementations de 15.625 msec (par defau sauf si appele synchro NTP ou manuelle )
    effectuées  sur les interuption systeme qui on lieu toute les 15.625 msec
    (PIT (ou du HPET) branchée sur IRQ 0 si timeBeginPeriod(15) (par defaut)
    ou  toutes les 16 interuptions de la RTC  RTC (ou du HPET)  branchée sur IRQ 8 si timeBeginPeriod(1)
    => petit cafouillage autour de timeBeginPerdiode(1))
    dans un entier 64-bit  correspondant au nombre de 100 nano-secondes (sans de tronquature)
    -  affecté par les ajustements manuelle de l'horloge windows ou apportés par la fonction GetSystemTimeAdjustment (synchro NTP)"""

    ft = LONG_INTEGER(0, 0)
    kernel32_GetSystemTimeAsFileTime(byref(ft))
    return (int(ft.high) << 32) | ft.low


# Time adjustement ---------------


def GetSystemTimeAdjustment():
    lpTimeAdjustment = c_long()
    lpTimeIncrement = c_long()
    lpTimeAdjustmentDisabled = c_long()
    kernel32_GetSystemTimeAdjustment(
        byref(lpTimeAdjustment), byref(lpTimeIncrement), byref(lpTimeAdjustmentDisabled)
    )
    return lpTimeAdjustment.value, lpTimeIncrement.value, lpTimeAdjustmentDisabled.value


def SetSystemTimeAdjustment(timeAdjustment):
    lpTimeAdjustment = c_long(timeAdjustment)
    lpTimeAdjustmentDisabled = c_long(False)
    return kernel32_SetSystemTimeAdjustment(lpTimeAdjustment, lpTimeAdjustmentDisabled)


# Mesures internes ---------------


def GetFileTimeAtStartUp():
    Tc1 = -1
    Tc2 = -2
    while Tc2 != Tc1:
        Tc1 = GetTickCount()
        FileTime = GetSystemTimeAsFileTime()
        Tc2 = GetTickCount()
    return FileTime - int(ceil(Tc1 / 15.625)) * 156250


FileTimeAtStartUp = GetFileTimeAtStartUp()


# conversion d'horloges incrementee sur interuption system toutes les 15.625 msec  -----------------------

# TickCount    nombre de millisecondes (a 15 msec prés)  qui se sont écoulés depuis le démarrage du système.		temps retourné par GetTickCount
# Tick 		nombre de tick system (tout les 15.625 msec) qui se sont écoulé depuis démarrage du système.
# AccurateTickCount     	nombre exacte en float de millisecondes (a 15 msec prés)  qui se sont écoulés depuis le démarrage du système.
# SystemTime	nombre de millisecondes (a 15 msec prés)  qui se sont écoulés depuis 1er janvier 1601. 			temps retourné par GetSystemTime
# Time         nombre de millisecondes (a 15 msec prés)  qui se sont écoulés depuis 1er janvier 1970. 			temps retourné par time.time()
# FileTime	nombre de 100 nano-secondes (a 15 msec prés)  qui se sont écoulés depuis 1er janvier 1601.		temps retourné GetSystemTimeAsFileTime (si y'a pas eu d'ajustements)
# Attention : FileTime correspondra au temps retourné par GetSystemTimeAsFileTime que si y'a pas eu d'ajustements !!!! (synchronisation manuelle ou via service de synchronisation NTP Windows )


def SystemTimeToFileTime(st):
    """cette conversion permet de regagner de la précision .
    Attention FileTime correspondra au temps retourné par GetSystemTimeAsFileTime que si y'a pas eu d'ajustements !!!! (synchronisation manuelle ou via service de synchronisation NTP Windows )"""
    return int(ceil(st / 15.625)) * 156250


def FileTimeToSystemTime(ft):
    """perd de la precision"""
    return int(ft * 0.0001)


def TimeToFileTime(t):
    """cette conversion permet de regagner de la précision et change date d'orgine 1970 -> 1601
    Attention FileTime correspondra au temps retourné par GetSystemTimeAsFileTime que si y'a pas eu d'ajustements !!!! (synchronisation manuelle ou via service de synchronisation NTP Windows )"""
    return SystemTimeToFileTime(TimeToSystemTime(t))


def TimeToSystemTime(t):
    """change date d'origine 1970 -> 1601"""
    return int(t * 1000) + 11644473600000


def TickCountToFileTime(Tc, FileTimeAtStartUp=FileTimeAtStartUp):
    """cette conversion permet de regagner de la précision .
    Attention FileTime correspondra au temps retourné par GetSystemTimeAsFileTime que si y'a pas eu d'ajustements !!!! (synchronisation manuelle ou via service de synchronisation NTP Windows )"""
    return int(ceil(Tc / 15.625)) * 156250 + FileTimeAtStartUp  # OK


def TickCountToTick(Tc):
    """converti getTickCount(millisecondes) en nombre de tick system depuis demarage"""
    return int(ceil(Tc / 15.625))


def TickToFileTime(T, FileTimeAtStartUp):
    """converti nombre de Tick system en FileTime.
    Attention FileTime correspondra au temps retourné par GetSystemTimeAsFileTime que si y'a pas eu d'ajustements !!!! (synchronisation manuelle ou via service de synchronisation NTP Windows )"""
    return T * 156250 + FileTimeAtStartUp


def TickCountToAccurateTickCount(Tc):
    """converti getTickCount(millisecondes) en version exacte (sans troncature à la milliseconde)"""
    return ceil(Tc / 15.625) * 15.625


# mes fonctions ------------------


def testSynchroNTP():  # pas encore codé
    pass
