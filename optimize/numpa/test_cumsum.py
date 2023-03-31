# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 00:04:35 2021

@author: Baptiste
"""
import numpy
from cumsum import cumsum
from time import perf_counter

red = "\033[38;2;255;0;0m"
green = "\033[38;2;0;255;0m"
no = "\033[0m"
blue = "\033[38;2;50;50;250m"
orange = "\033[38;2;255;200;0m"


def test_cumsum():
    print("cumsum")
    for shape in [(9, 10), (152, 150), (640, 480), (640, 480, 3)]:
        print(f"   shape {shape}")
        for axis in [0, 1]:
            print(f"        axis {axis}")
            for order in ["c", "f"]:
                print(f"            {order} order")
                a = numpy.random.randint(0, 255, size=shape, dtype="uint8")
                b = numpy.random.randint(0, 255, size=shape, dtype="uint8")
                if order == "f":
                    a = numpy.asfortranarray(a)
                    b = numpy.asfortranarray(b)
                # a_orginal = a

                numpy_times = {}
                numpa_times = {}
                numpy_median = {}
                numpa_median = {}
                color = {}
                for inplace in [False, True]:
                    if inplace:
                        out = a
                    else:
                        out = None
                    numpy_times[inplace] = []
                    numpa_times[inplace] = []

                    for i in range(1000):
                        start = perf_counter()
                        numpy_value = numpy.cumsum(a, axis=axis, dtype=a.dtype, out=out)
                        end = perf_counter()
                        numpy_times[inplace].append(end - start)

                    for i in range(1000):
                        start = perf_counter()
                        numpa_value = cumsum(a, axis=axis, out=out)
                        end = perf_counter()
                        numpa_times[inplace].append(end - start)
                        if i == 0:
                            assert numpy.all(numpy_value == numpa_value)

                    numpy_median[inplace] = numpy.median(numpy_times[inplace])
                    numpa_median[inplace] = numpy.median(numpa_times[inplace])

                    if numpa_median[inplace] < numpy_median[inplace] * 0.9:
                        color[inplace] = green
                    elif numpa_median[inplace] > numpy_median[inplace] * 0.1:
                        color[inplace] = red
                    else:
                        color[inplace] = no
                print(
                    f"                numpy {numpy_median[False]*1000:.3f} msec    Inplace {numpy_median[True]*1000:.3f} msec{no}"
                )
                print(
                    f"                {color[False]}numpa {numpa_median[False]*1000:.3f} msec    {color[True]}Inplace {numpa_median[True]*1000:.3f} msec{no}"
                )

    print("test_cumsum passed")


if __name__ == "__main__":
    test_cumsum()
