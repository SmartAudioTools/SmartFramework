import cv2
from SmartFramework.files import splitPath, joinPath, changeExt, addToName, searchExt
from SmartFramework.serialize import serializejson
import numpy
from time import perf_counter
import pickle
import blosc
import os
import soundfile

blosc_compressions = {
    (name if name == "blosclz" else "blosc_" + name): name for name in blosc.cnames
}


# audioPath = "D:/Dropbox/Musique/BEST OF SOIREE/METAL/System of a Down - Toxicity.flac"
audioPaths = searchExt(
    "D:/Dropbox/Musique/BEST OF SOIREE/ROCK - Copie", "flac"
)  # "Christian Löffler - Ash & Snow.flac"
codecs = [
    "blosc_zstd",
    # "wav",
    # "flac",
    # "json",
    # "pickle",
]  # "blosc_zstd","json","wav","flac"]
blosc_diff_temporel = True
# @profile
def __main__():
    for audioPath in audioPaths:
        sound, samplerate = soundfile.read(audioPath, dtype="int16")
        for codec in codecs:
            codec_is_losless = True
            if codec in ["wav", "flac"]:
                if codec == "flac":
                    outPath = addToName(audioPath, codec)
                else:
                    outPath = changeExt(audioPath, codec)
                start_write = perf_counter()
                soundfile.write(outPath, sound, samplerate)
                end_write = perf_counter()
                start_read = perf_counter()
                new_sound, new_samplerate = soundfile.read(outPath, dtype="int16")
                end_read = perf_counter()
                if not numpy.all(sound == new_sound):
                    codec_is_losless = False

            elif codec == "json":
                outPath = changeExt(audioPath, codec)
                start_write = perf_counter()
                serializejson.dump(
                    sound, outPath, bytes_compression=("blosc_zstd", 4)
                )  # ,bytes_compression_diff_dtypes = ("int16",))
                end_write = perf_counter()
                start_read = perf_counter()
                new_sound = serializejson.load(outPath)
                end_read = perf_counter()
                if not numpy.all(sound == new_sound):
                    codec_is_losless = False

            elif codec.startswith("blosc"):
                for n in [0, 1, 2, 3]:
                    outPath = changeExt(audioPath, f"{codec}_n{n}")
                    start_write = perf_counter()
                    shape_len = sound.shape
                    if blosc_diff_temporel:
                        data = numpy.diff(
                            sound,
                            axis=0,
                            prepend=numpy.uint8([[0, 0]] * n),
                            n=n,
                        )
                        # data = numpy.diff(sound,axis=0,prepend=sound[:1],n=2)
                    else:
                        data = sound
                        # data = numpy.ediff1d(sound,to_begin=sound.flat[0])
                    blosc_compression = blosc_compressions.get(codec, None)
                    blosc.set_nthreads(8)
                    compressed = blosc.compress(
                        numpy.ascontiguousarray(data),
                        data.itemsize,
                        cname=blosc_compression,
                        clevel=4,
                    )

                    outFile = open(outPath, "wb")
                    outFile.write(compressed)
                    outFile.close()
                    end_write = perf_counter()
                    start_read = perf_counter()
                    outFile = open(outPath, "rb")
                    compressed = outFile.read()
                    decoded_bytearray = blosc.decompress(compressed, as_bytearray=True)
                    decompressed = numpy.ndarray(shape_len, "int16", decoded_bytearray)
                    if blosc_diff_temporel:
                        for i in range(n):
                            numpy.cumsum(
                                decompressed,
                                axis=0,
                                dtype="int16",
                                out=decompressed,
                            )  # super long !!!!

                    # else :
                    #    decompresse =
                    #    numpy.cumsum(decompressed.flat,out=decompressed.ravel())
                    if not numpy.all(sound == decompressed):
                        codec_is_losless = False
                    outFile.close()
                    end_read = perf_counter()

            elif codec == "pickle":
                outPath = changeExt(audioPath, codec)
                start_write = perf_counter()
                outFile = open(outPath, "wb")
                pickle.dump(sound, outFile)
                outFile.close()
                end_write = perf_counter()
                start_read = perf_counter()
                outFile = open(outPath, "rb")
                pickle.load(outFile)
                outFile.close()
                end_read = perf_counter()
            else:
                continue
            if codec_is_losless:
                print(f"{codec} is losless")
            else:
                print(f"{codec} is NOT losless")
            print(
                f"     {(end_write - start_write)*1000/ (len(sound)/samplerate)} msec to write a second of sound"
            )
            print(
                f"     {(end_read - start_read)*1000/ (len(sound)/samplerate)} msec to read a second of sound"
            )


__main__()

__main__()
