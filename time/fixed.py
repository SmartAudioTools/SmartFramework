# -*- coding: utf-8 -*-
""" module permetant conversion entre float et nombre à virgule fixé a 32 bits """


# float 	secondes décimale		(float)
# fixed	    seconde virgule fixée à 32 bits (int 64 bits)

# int   	secondes entières		( int 32 bits )
# dec       sub-secondes 			( float [0.-1.[ )
# frac  	sub-secondes 			( int 32 bits )


# retourne fixed   ----------


def fixedFromFloat(f):
    return int(f * 2.0**32)


def fixedFromIntFrac(i, fr):
    return i << 32 | fr
    # return i * 2**32 + d


def fixedFromIntDec(i, d):
    return i << 32 | int(dec * 2.0**32)
    # return i * 2**32 + d


# retourne tuple -----------------
def fixedFloatFromFloat(f):
    return int(f * 2.0**32), f - (int(f * 2.0**32) * 2**-32)


# retourne float   ----------


def floatFromFixed(fix):
    return fix * 2.0**-32


def floatFromIntFrac(i, fr):
    return float(i << 32 + fr) * 2.0**-32


def floatFromIntDec(i, d):
    return i + d


# int/frac/dec-------------------

# from Float
def intFromFloat(f):
    return int(f)


def fracFromFloat(f):
    return int(f * 2.0**32) - int(f) << 32  # a verifier
    # int(abs(date - to_int(date)) * 2**n)


def decFromFloat(f):
    return f - int(f)


# from Fixed


def intFromFixed(fix):
    return fix >> 32


def fracFromFixed(fix):
    return fix - (fix >> 32 << 32)


def decFromFixed(fix):
    return (fix - (fix >> 32 << 32)) * 2.0**-32
