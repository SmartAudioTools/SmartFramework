# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 23:53:22 2020

@author: Baptiste
"""
import sys
import numpy

bytes_ = bytes(range(255))
bytes_array = numpy.frombuffer(bytes_, numpy.uint8)
string = bytes_.decode("utf-8")
bytes_array.flags.writeable = True
bytes_array[0] += 1
print(bytes_)
print(sys.getsizeof(bytes_))
print(string)
print(sys.getsizeof(string))
