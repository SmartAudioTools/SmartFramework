# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 00:04:35 2021

@author: Baptiste
"""
import numpy
from diff import diff
from time import perf_counter

red = "\033[38;2;255;0;0m"
green = "\033[38;2;0;255;0m"
no = "\033[0m"
blue = "\033[38;2;50;50;250m"
orange = "\033[38;2;255;200;0m"


def test_diff():
    print("diff")
    for shape in [(9, 10), (152, 150), (640, 480), (6400, 4800), (640, 480, 3)]:
        test_nb = int(max(min(60000000 / numpy.product(shape), 2000), 9))
        print(f"    shape {shape}")
        for axis in [0, 1]:
            print(f"        axis {axis}")
            for order in ["c", "f"]:
                print(f"            {order} order")

                a = numpy.random.randint(0, 255, size=shape, dtype="uint8")
                b = numpy.random.randint(0, 255, size=shape, dtype="uint8")
                if order == "f":
                    a = numpy.asfortranarray(a)
                    b = numpy.asfortranarray(b)
                a_orginal = a

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
                    numpy_times = []
                    numpa_times[inplace] = []

                    if inplace is False:
                        for i in range(test_nb):
                            start = perf_counter()
                            numpy_value = numpy.diff(
                                a, axis=axis, prepend=numpy.uint8(0)
                            )
                            end = perf_counter()
                            numpy_times.append(end - start)
                        numpy_median = numpy.median(numpy_times)

                    for i in range(test_nb):
                        a_copy = a.copy()
                        start = perf_counter()
                        numpa_value = diff(a_copy, axis=axis, out=out)
                        end = perf_counter()
                        numpa_times[inplace].append(end - start)
                        if i == 0:
                            assert numpy.all(numpy_value == numpa_value)

                    numpa_median[inplace] = numpy.median(numpa_times[inplace])

                    if numpa_median[inplace] < numpy_median * 0.9:
                        color[inplace] = green
                    elif numpa_median[inplace] > numpy_median * 0.1:
                        color[inplace] = red
                    else:
                        color[inplace] = no
                print(f"                numpy {numpy_median*1000:.2f} msec ")

                print(
                    f"                {color[False]}numpa {numpa_median[False]*1000:.3f} msec    {color[True]}Inplace {numpa_median[True]*1000:.3f} msec{no}"
                )

    print("test_diff passed")


if __name__ == "__main__":

    test_diff()
