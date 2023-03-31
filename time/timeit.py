# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 09:44:46 2018

@author: Baptiste
"""
from timeit import Timer
from time import perf_counter


def timeit(stmt, setup="pass", number=None, repeat=None, evalTime=5.0, repeatMax=1000):
    timer = Timer(stmt=stmt, setup=setup)

    if number is not None:
        if repeat is not None:
            return min(timer.repeat(repeat=repeat, number=number)) / number
        else:
            return timer.timeit(number=number) / number
    else:
        tBefore = perf_counter()
        timeOne = timer.timeit(number=1)
        timeOneWithSetup = perf_counter() - tBefore
        # timeSetup = timeOne -timeOneWithSetup
        nbRepeatPossible = round(evalTime / timeOneWithSetup)
        if nbRepeatPossible == 1:
            return timeOne
        repeat = min(repeatMax, nbRepeatPossible)
        # int((evalTime - repeat * timeSetup) /  timeOne)
        number = int(nbRepeatPossible / repeat)
        #  liste du temps que chaque cycle de test a pris
        times = timer.repeat(repeat=repeat, number=number)
        # minimum sur 3 essais,  du temps moyen par appel en secondes
        return min(times) / number


if __name__ == "__main__":

    print(
        timeit(
            "b = numpy.rot90(a,2);c = numpy.ascontiguousarray(b)",
            "import numpy;a = numpy.ones((640,480),numpy.uint8)",
        )
        * 1000.0,
        " msec",
    )
