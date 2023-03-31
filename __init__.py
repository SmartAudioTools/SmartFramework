"""
import sip
API_NAMES = ["QDate", , "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
API_VERSION = 2
for name in API_NAMES:
    sip.setapi(name, API_VERSION)


#------- Imports Bibliotheque Tierces ------------

import sys
import timer 
import numpy
from   qtpy import QtCore, QtGui,uic
import os.path

#------- Imports Bibliotheque SmartFramework ------------
import audio
import events
import ui
import video
import par
#import tools
import designer
import midi
#------------------
"""
from pybase64 import b64decode, b64decode_as_bytearray
from numpy import frombuffer, unpackbits, uint8, ndarray, int32, int64
from numpy import dtype as numpy_dtype
from SmartFramework.serialize import serialize_parameters
import array
import sys
import blosc

try:
    profile
except:

    def profile(func):
        return func

else:
    profile = profile

blosc_compressions = set(blosc.cnames)

# defaultIntType =  numpy_dtype("int_")
nb_bits = sys.maxsize.bit_length() + 1
is_64_bit = nb_bits == 64


def bytearrayB64(b64, compression=None):
    if compression:
        if compression in blosc_compressions:
            return blosc.decompress(b64decode(b64, validate=True), as_bytearray=True)
        raise Exception(f"unknow {compression} compression")
    return b64decode_as_bytearray(b64, validate=True)


def bytesB64(b64, compression=None):
    if compression:
        if compression in blosc_compressions:
            return blosc.decompress(b64decode(b64, validate=True))
        raise Exception(f"unknow {compression} compression")
    return b64decode(b64, validate=True)


def numpyB64(str64, dtype=None, shape_len_compression=None, compression=None):
    decoded_bytearray = b64decode_as_bytearray(str64, validate=True)
    if isinstance(shape_len_compression, str):
        compression = shape_len_compression
        shape_len = None
    else:
        shape_len = shape_len_compression
    if compression:
        if compression in blosc_compressions:
            decoded_bytearray = blosc.decompress(decoded_bytearray, as_bytearray=True)
        else:
            raise Exception(f"unknow {compression} compression")
    if dtype in ("bool", bool):
        # pas de copie -> read only :
        numpy_uint8_containing_8bits = frombuffer(decoded_bytearray, uint8)
        # copie dans un numpy array de uint8 mutable :
        numpy_uint8_containing_8bits = unpackbits(numpy_uint8_containing_8bits)
        if shape_len is None:
            shape_len = len(numpy_uint8_containing_8bits)
        return ndarray(shape_len, dtype, numpy_uint8_containing_8bits)  # pas de recopie
    else:
        if isinstance(dtype, list):
            dtype = [(str(champName), champType) for champName, champType in dtype]
        if shape_len is None:
            array = frombuffer(decoded_bytearray, dtype)  # pas de recopie
        else:
            array = ndarray(shape_len, dtype, decoded_bytearray)  # pas de recopie
        if (
            nb_bits == 32
            and serialize_parameters.numpyB64_convert_int64_to_int32_and_align_in_Python_32Bit
        ):
            # pour pouvoir deserialiser les classifiers en python 32 bit ?
            if array.dtype in (int64, "int64"):
                return array.astype(int32)
            elif isinstance(dtype, list):
                newTypes = []
                for champ in dtype:
                    champName, champType = champ
                    if champName:
                        champType = numpy_dtype(champType)
                        if champType in (int64, "int64"):
                            newTypes.append((champName, int32))
                        else:
                            newTypes.append((champName, champType))
                newDtype = numpy_dtype(newTypes, align=True)
                newN = ndarray(len(array), newDtype)
                for champName, champType in newTypes:
                    if champName:
                        newN[champName][:] = array[champName]
                return newN
        return array


def arrayB64(str64, typecode, compression=None):
    decoded_bytearray = b64decode_as_bytearray(str64, validate=True)
    if compression:
        if compression in blosc_compressions:
            decoded_bytearray = blosc.decompress(decoded_bytearray, as_bytearray=True)
        else:
            raise Exception(f"unknow {compression} compression")
    # A REVOIR fait une copie même avec decoded_bytearray
    return array.array(typecode, decoded_bytearray)


fromB64 = numpyB64  # pour pouvoir ouvrir d'anciens fichiers serializÃ©s
