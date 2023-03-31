# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:17:46 2020

@author: Baptiste
"""

import ctypes

# https://github.com/abarnert/superhackyinternals/blob/master/internals.py


class PyUnicodeObject(ctypes.Structure):
    SSTATE_NOT_INTERNED = 0
    SSTATE_INTERNED_MORTAL = 1
    SSTATE_INTERNED_IMMORTAL = 2
    PyUnicode_WCHAR_KIND = 0
    PyUnicode_1BYTE_KIND = 1
    PyUnicode_2BYTE_KIND = 2
    PyUnicode_4BYTE_KIND = 4

    class LegacyUnion(ctypes.Union):
        _fields_ = (
            ("any", ctypes.c_void_p),
            ("latin1", ctypes.POINTER(ctypes.c_uint8)),  # Py_UCS1 *
            ("ucs2", ctypes.POINTER(ctypes.c_uint16)),  # Py_UCS2 *
            ("ucs4", ctypes.POINTER(ctypes.c_uint32)),
        )  # Py_UCS4 *

    _fields_ = (
        ("ob_refcnt", ctypes.c_ssize_t),
        ("ob_type", ctypes.c_void_p),
        # Note that it's not a PyVarObject; length instead of ob_size,
        # which is the length in code points of the actual string,
        # regardless of how it's stored internally.
        ("length", ctypes.c_ssize_t),
        ("hash", ctypes.c_int64),  # actually Py_hash_t == intptr_t
        ("interned", ctypes.c_uint, 2),  # SSTATE_*
        ("kind", ctypes.c_uint, 3),  # PyUnicode_*_KIND
        ("compact", ctypes.c_uint, 1),
        ("ascii", ctypes.c_uint, 1),
        ("ready", ctypes.c_uint, 1),
        ("padding", ctypes.c_uint, 24),
        ("wstr", ctypes.POINTER(ctypes.c_wchar)),
        # Fields after this do not exist if ascii
        ("utf8_length", ctypes.c_ssize_t),
        ("utf8", ctypes.c_char_p),
        ("wstr_length", ctypes.c_ssize_t),
        # Fields after this do not exist if compact
        ("data", LegacyUnion),
    )

    """_KINDS = {
        PyUnicodeObject.PyUnicode_WCHAR_KIND: ctypes.c_wchar,
        PyUnicodeObject.PyUnicode_1BYTE_KIND: ctypes.c_uint8,
        PyUnicodeObject.PyUnicode_2BYTE_KIND: ctypes.c_uint16,
        PyUnicodeObject.PyUnicode_4BYTE_KIND: ctypes.c_uint32,
        }"""


def StringInside(string):
    return PyUnicodeObject.from_address(id(string))


stringInside = StringInside("coucou")
