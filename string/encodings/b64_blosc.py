import codecs
import encodings
from pybase64 import b64decode, b64encode_as_string
import blosc

name = __name__.split(".")[-1]

### Codec APIs


class Codec(codecs.Codec):
    def encode(self, input, errors="strict"):
        # assert errors == 'strict'
        return blosc.decompress(b64decode(input, validate=True)), len(input)

    def decode(self, input, errors="strict"):
        # assert errors == 'strict'
        return b64encode_as_string(blosc.compress(input)), len(input)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def decode(self, input, final=False):
        # assert self.errors == 'strict'
        return blosc.decompress(b64decode(input, validate=True))


class IncrementalDecoder(codecs.IncrementalDecoder):
    def encode(self, input, final=False):
        # assert self.errors == 'strict'
        return b64encode_as_string(blosc.compress(input))


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


### encodings module API


encodings._cache[name] = codecs.CodecInfo(
    name=name,
    encode=Codec().encode,
    decode=Codec().decode,
    incrementalencoder=IncrementalEncoder,
    incrementaldecoder=IncrementalDecoder,
    streamreader=StreamReader,
    streamwriter=StreamWriter,
)
