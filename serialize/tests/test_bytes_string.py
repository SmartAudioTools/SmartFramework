import rapidjson

# import rapidjsonbytes
import copy
import io
import pickle
from collections import deque
from SmartFramework.serialize import serializejson


class Stream:
    def __init__(self):
        self._deque = deque()

    def write(self, elt):
        self._deque.append(elt)


@profile
def test_RawJSON():

    # string
    str1 = f'"[{"0,"*60000000}0]"'  # 71 msec
    str2 = str1 + "\u25B8"  # 74 msec
    bytes1 = str1.encode("utf_8")  # 32 msec
    bytes2 = str2.encode("utf_8")  # 120 msec
    rawstring1 = rapidjson.RawString(str1)  # 0.01 msec
    rawstring2 = rapidjson.RawString(str2)  # 0.01 msec
    rawbytes1 = rapidjson.RawBytes(bytes1)  # 0.01 msec
    rawbytes2 = rapidjson.RawBytes(bytes2)  # 0.01 msec

    # copies
    bytes1_copie = bytes1 + b"_"  # 32 msec
    str1_copie = str1 + "_"  # 32 msec

    # pickle =================================================================
    pickle.dumps(str1)  # 38 msec
    pickle.dumps(str2)  # 196 msec
    pickle.dumps(bytes1)  # 38 msec
    pickle.dumps(bytes2)  # 38 msec

    stream1, stream2, stream3, stream4 = Stream(), Stream(), Stream(), Stream()
    pickle.dump(str1, stream1)  # 32 msec
    pickle.dump(str2, stream3)  # 32  msec
    pickle.dump(bytes1, stream2)  # 0.01 msec
    pickle.dump(bytes2, stream4)  # 0.01 msec

    # serializejson  ======================================================
    serializejson.dumpb(str1, indent=None)  #  142 msec (490 msec avant optimisation)
    serializejson.dumpb(str2, indent=None)  #  142 msec( 490 msec avant optimisation)
    serializejson.dumpb(bytes1, indent=None)  # 22 msec
    serializejson.dumpb(bytes2, indent=None)  # 20 msec
    serializejson.dumpb(rawbytes1, indent=None)  # 38 msec !?
    serializejson.dumpb(rawbytes2, indent=None)  # 39 msec !?

    stream = Stream()
    # 103 msec (513 msec avant optimisation):
    serializejson.dump(str1, stream, indent=None)
    # 103 msec (513 msec avant optimisation):
    serializejson.dump(str2, stream, indent=None)
    serializejson.dump(bytes1, stream, indent=None)  # 20 msec
    serializejson.dump(bytes2, stream, indent=None)  # 20 msec
    serializejson.dump(rawbytes1, stream, indent=None)  # 0.07 msec
    serializejson.dump(rawbytes2, stream, indent=None)  # 0.04 msec

    serializejson.dumpb(str1)  # 142 msec (513 msec avant optimisation)
    serializejson.dumpb(str2)  # 142 msec (513 msec avant optimisation)
    serializejson.dumpb(bytes1)  # 22 msec
    serializejson.dumpb(bytes2)  # 20 msec
    serializejson.dumpb(rawbytes1)  # 38 msec !?
    serializejson.dumpb(rawbytes2)  # 39 msec !?

    stream = Stream()
    serializejson.dump(str1, stream)  # 103 msec (513 msec avant optimisation)
    serializejson.dump(str2, stream)  # 103 msec (513 msec avant optimisation)
    serializejson.dump(bytes1, stream)  # 20 msec
    serializejson.dump(bytes2, stream)  # 20 msec
    serializejson.dump(rawbytes1, stream)  # 0.07 msec
    serializejson.dump(rawbytes2, stream)  # 0.04 msec

    # Rapidjson modifié ====================================================

    # sortie bytes
    bytes_str1 = rapidjson.dumps(str1, ensure_ascii=False, return_bytes=True)
    bytes_str2 = rapidjson.dumps(str2, ensure_ascii=False, return_bytes=True)
    # 32 msec (646 msec before optimisations):
    bytes_rawstring1 = rapidjson.dumps(
        rawstring1, ensure_ascii=False, return_bytes=True
    )
    # 32 msec (646 msec before optimisations):
    bytes_rawbytes1 = rapidjson.dumps(rawbytes1, ensure_ascii=False, return_bytes=True)
    # 236 ou 74 msec en fonction de là où placé !? (646 msec before optimisations):
    bytes_rawstring2 = rapidjson.dumps(
        rawstring2, ensure_ascii=False, return_bytes=True
    )
    # 32 msec (646 msec before optimisations):
    bytes_rawbytes2 = rapidjson.dumps(rawbytes2, ensure_ascii=False, return_bytes=True)

    # sortie string
    str_str1 = rapidjson.dumps(str1, ensure_ascii=False, return_bytes=True)
    str_str2 = rapidjson.dumps(str2, ensure_ascii=False, return_bytes=True)
    # 70 msec (646 msec before optimisations):
    str_rawstring1 = rapidjson.dumps(rawstring1, ensure_ascii=False)
    # 70 msec (646 msec before optimisations):
    str_rawbytes1 = rapidjson.dumps(rawbytes1, ensure_ascii=False)
    # 324 ou 162 msec  en fonction de là où placé !?(646 msec before optimisations):
    str_rawstring2 = rapidjson.dumps(rawstring2, ensure_ascii=False)
    # 182 msec (646 msec before optimisations):
    str_rawbytes2 = rapidjson.dumps(rawbytes2, ensure_ascii=False)

    # sortie File
    stream1, stream2, stream3, stream4 = Stream(), Stream(), Stream(), Stream()
    # 32 msec (646 msec before optimisations):
    rapidjson.dump(rawstring1, stream1, ensure_ascii=False)
    rapidjson.dump(rawstring2, stream2, ensure_ascii=False)  # 32
    rapidjson.dump(rawbytes1, stream3, ensure_ascii=False)  # 0.01 msec
    rapidjson.dump(rawbytes2, stream4, ensure_ascii=False)  #  0.01 msec

    assert str1 == str_rawstring1
    assert str1 == str_rawbytes1
    assert str2 == str_rawstring2
    assert str2 == str_rawbytes2
    assert bytes1 == bytes_rawstring1
    assert bytes1 == bytes_rawbytes1
    assert bytes2 == bytes_rawstring2
    assert bytes2 == bytes_rawbytes2


test_RawJSON()
# print(type(with_rawstring))
# print(with_rawstring[:10])
