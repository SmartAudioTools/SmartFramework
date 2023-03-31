# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 14:31:51 2011

@author: guilbut
"""
"""

class Time(float):
    pass
   
"""
"""
class Time(): 
    def __init__(self, msec = 0.0):
        self.msec = msec
    def __cmp__(self, other):
        return cmp(self.msec,other.msec)
    def __add__(self, other):
        return Time(self.msec + other.msec)

"""


def addTimeTuple(time1, time2):
    sumsubmsec = time1[1] + time2[1]
    if sumsubmsec < 1.0:
        return (time1[0] + time2[0], sumsubmsec)
    else:
        return (time1[0] + time2[0] + 1, sumsubmsec - 1.0)


def TimeTuple(msec=0, submsec=0.0):
    if type(msec) == float:
        submsecfrommsec = msec - int(msec)
        msec = int(msec)
        submsec = submsec + submsecfrommsec
        if sumsubmsec > 1.0:
            submsec = submsec - 1.0
    return (msec, submsec)


class TimeObj:
    def __init__(self, msec=0, submsec=0.0):
        self.__dict__.update(locals())
        if type(msec) == float:
            submsecfrommsec = msec - int(msec)
            msec = int(msec)
            sumsubmsec = submsec + submsecfrommsec
            if sumsubmsec < 1.0:
                self.msec = msec
                self.submsec = sumsubmsec
            else:
                self.msec = msec + 1
                self.submsec = sumsubmsec - 1.0

    def __cmp__(self, other):
        return cmp((self.msec, self.submsec), (other.msec, other.submsec))

    def __add__(self, other):
        sumsubmsec = self.submsec + other.submsec
        if sumsubmsec < 1.0:
            return Time(self.msec + other.msec, sumsubmsec)
        else:
            return Time(self.msec + other.msec + 1, sumsubmsec - 1.0)

    def __sub__(self, other):
        submsec = self.submsec - other.submsec
        if sumsubmsec > 0.0:
            return Time(self.msec - other.msec, submsec)
        else:
            return Time(self.msec - other.msec - 1, sumsubmsec + 1.0)
