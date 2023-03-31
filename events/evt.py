# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 14:32:21 2011

@author: guilbut
"""
from SmartFramework.events.time import Time


class Evt:
    def __init__(self, time, slot, data=None, priority=0):
        self.__dict__.update(locals())

    def __cmp__(self, other):
        return cmp((self.time, self.priority), (other.time, other.priority))

        sumsubmsec = self.submsec + other.submsec
        if sumsubmsec < 1.0:
            return Time(self.msec + other.msec, sumsubmsec)
        else:
            return Time(self.msec + other.msec + 1, sumsubmsec - 1.0)
