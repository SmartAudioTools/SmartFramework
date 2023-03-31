# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 18:23:00 2021

@author: Baptiste
"""

import numpy
from numba import njit, prange
from SmartFramework import is_64_bit


@njit(cache=True, parallel=is_64_bit)
def subtract(x1, x2, out=None, dtype=None):
    "le inplace n'apporte rien par contre on cagne en 2D sur numpy"
    height, width = x1.shape[:2]
    if out is None:
        if dtype is None:
            _dtype = x1.dtype
        else:
            _dtype = dtype
        _out = numpy.empty(x1.shape, dtype=_dtype)
    else:
        _out = out
    for i in prange(height):
        _out[i] = x1[i] - x2[i]  # 0.127 msec pour du 640x480
        # x1[i] -= x2[i]  # 0.139 msec pour du 640x40
    return _out


"""
# compile or load cashed numpa function
dtypes = [numpy.uint8]
shapes = ((10, 10), (10, 10, 3))
for dtype in dtypes:
    for shape in shapes:
        for order in ["c", "f"]:
            a = numpy.empty(shape, dtype=dtype, order=order)
            b = numpy.empty(shape, dtype=dtype, order=order)
            out = subtract(a, b)
            subtract(a, b, out=out)
"""
