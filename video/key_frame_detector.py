"""
numpy like with :
- fonction multithreaded with numba
- "out" and "inplace" (overwriting first array)  optionnal parameter when possible
"""


import numpy
from numba import njit, prange
from SmartFramework import is_64_bit


@njit(cache=True, parallel=is_64_bit)
def key_frame_detector(new, key, step):
    if new.shape != key.shape:
        return True
    sum_diff_temp = 0
    sum_diff_spacial = 0
    new_ = new.view(numpy.int8)
    key_ = key.view(numpy.int8)
    height, width = new.shape[:2]
    for index in prange(int(height / step)):
        i = index * step
        line_diff_temp = 0
        line_diff_spacial = 0
        for j in range(0, width - 1, step):
            line_diff_temp += abs(new_[i, j] - key_[i, j])
            line_diff_spacial += abs(new_[i, j] - new_[i, j + 1])
        sum_diff_temp += line_diff_temp
        sum_diff_spacial += line_diff_spacial
    return sum_diff_spacial < sum_diff_temp


# compile or load cashed numpa function
# a = numpy.empty((640, 480), dtype="uint8")
# b = numpy.empty((640, 480), dtype="uint8")
# key_frame_detector(a, b, 8)
