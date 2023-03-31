# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 18:23:00 2021

@author: Baptiste
"""

import numpy
from numba import njit, prange
from SmartFramework import is_64_bit


@njit(cache=True, parallel=is_64_bit)
def cumsum(a, axis=None, dtype=None, out=None):  # , inplace = False):
    inplace = out is a
    shape = a.shape
    height = shape[0]
    width = shape[1]
    if out is None:
        if dtype is None:
            _dtype = a.dtype
        else:
            _dtype = _dtype
        _out = numpy.empty(a.shape, dtype=_dtype)
    else:
        _out = out
    if axis == 0:
        if inplace:
            for j in prange(width):
                for i in range(1, height):
                    # pourrait être encore optimisé
                    a[i, j] += a[i - 1, j]
        else:
            for j in prange(width):
                _out[0, j] = a[0, j]
                for i in range(1, height):
                    # pourrait être encore optimisé
                    _out[i, j] = a[i, j] + _out[i - 1, j]
    elif axis == 1:
        if inplace:
            for i in prange(height):
                for j in range(1, width):
                    # pourrait être encore optimisé
                    a[i, j] += a[i, j - 1]
        else:
            for i in prange(height):
                # pourrait être encore optimisé
                _out[i, 0] = a[i, 0]
                for j in range(1, width):
                    _out[i, j] = a[i, j] + _out[i, j - 1]
    else:
        raise Exception(
            "numpa.cumsum is not fully coded and does'nt support other axis than 0 and 1 yet"
        )
    return _out


""" Empeche import..
# compile or load cashed numpa function
dtypes = [numpy.uint8]
shapes = ((10, 10), (10, 10, 3))
for dtype in dtypes:
    for shape in shapes:
        for axis in [0, 1]:
            for order in ["c", "f"]:
                a = numpy.empty(shape, dtype=dtype, order=order)
                b = numpy.empty(shape, dtype=dtype, order=order)
                out = cumsum(a, 1)
                cumsum(a, axis, out=out)"""
