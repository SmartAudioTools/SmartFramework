# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 18:23:00 2021

@author: Baptiste
"""

import numpy
from numba import njit, prange
from SmartFramework import is_64_bit


@njit(cache=True, parallel=is_64_bit)
def add(x1, x2, out=None, dtype=None):
    height, width = x1.shape[:2]
    if out is None:
        if dtype is None:
            _dtype = x1.dtype
        else:
            _dtype = _dtype
        _out = numpy.empty(x1.shape, dtype=_dtype)
    else:
        _out = out
    for i in prange(height):
        _out[i] = x1[i] + x2[i]
        # x1[i] += x2[i]  # pas mieux pour du inplace
    # nb_thread = 8
    # block_size = math.ceil(len(x1) / nb_thread)
    # for t in prange(8):
    #    start = t * block_size
    #    stop = (t + 1) * block_size
    #    _out[start:stop] = x1[start:stop] + x2[start:stop]
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
            out = add(a, b)
            add(a, b, out=out)"""
