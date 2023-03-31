import cv2
import os
import numpy
import math
from time import perf_counter
from SmartFramework.string import red, lime, blue, orange, no_color
from SmartFramework.files import splitPath, joinPath
from SmartFramework.serialize import serializejson
from SmartFramework.video.codecs import codec_names  # add ZSTD and PICK codec to opencv

# solution sans remplacemtn de cv2.VideoCapture et cv2.VideoCapture:
# from SmartFramework.video.VideoCapture import VideoCapture
# from SmartFramework.video.VideoWriter import VideoWriter, codec_names


videoPaths = ["Baptiste.avi"]

codecs_with_comment = {
    # Codecs ajouté par SmartFramework
    "PICK": "serialisation directe des frames dans fichier avec pickle",
    "ZSTD": "diff + compression avec blosc zstd streamé dans fichier binaire",
    "json": "frames directement streamées dans un json (avec serializejson parametré pour faire de la diff spacial sur image et qui compresse avec blosc)",
    # Codecs opencv
    "DIB ": f"{lime}losless\n     {red}sans compression et ne marche plus avec opencv 4{no_color}",
    "LAGS": f"{lime}losless\n     rapide, compact, suporté par miniatures windows, VLC et Media Player Classic\n     {red}mais ne marche plus avec opencv > {no_color}",
    "H264": f"{red}Je n'arrive pas à la faire marcher{no_color}",
    "bmp": "",
    "png": "",
    "jpg": "",
    "FFV1": "",
    "HFYU": "",
    "YUV4": f"{red}pas compatible VLC et Media Player Classic{no_color}",
    "TIFF": f"{red}pas compatible VLC et Media Player Classic{no_color}",
    "MJPG": "",
    "DIVX": "",
    "MP4V": "",
    "XVID": "",
    "ASV1": "",
    "ASV2": "",
    "SNOW": "",
    "WMV1": "",
    "WMV2": "",
}

# codecs que je n'arrive pas à la faire marcher
[
    "AVC1",
    "ALAC",
    "APNG",
    "APTX",
    "AVRP",
    "AVUI",
    "AYUV",
    "CLJR",
    "EAC3",
    "FITS",
    "FLAC",
    "H261",
    "H263",
    "R10K",
    "R210",
    "RV10",
    "RV20",
    "SVQ1",
    "TEXT",
    "V210",
    "V308",
    "V408",
    "V410",
    "Y41P",
    "ZLIB",
    "XSUB",
    "ZMBV",
    "A64MULTI",
    "A64MULTI5",
    "AAC",
    "AC3",
    "AC3_FIXED",
    "ADPCM_ADX",
    "ADPCM_G722",
    "ADPCM_G726",
    "ADPCM_G726LE",
    "ADPCM_IMA_QT",
    "ADPCM_IMA_WAV",
    "ADPCM_MS",
    "ADPCM_SWF",
    "ADPCM_YAMAHA",
    "ALIAS_PIX",
    "AMV",
    "APTX_HD",
    "ASS",
    "BMP",
    "CINEPAK",
    "COMFORTNOISE",
    "DCA",
    "DNXHD",
    "DPX",
    "DVBSUB",
    "DVDSUB",
    "DVVIDEO",
    "FFVHUFF",
    "FLASHSV",
    "FLASHSV2",
    "FLV",
    "G723_1",
    "GIF",
    "H263P",
    "HUFFYUV",
    "JPEG2000",
    "JPEGLS",
    "LIBVPX_VP8",
    "LIBVPX_VP9",
    "LJPEG",
    "MAGICYUV",
    "MJPEG",
    "MLP",
    "MOVTEXT",
    "MP2",
    "MP2FIXED",
    "MPEG1VIDEO",
    "MPEG2VIDEO",
    "MPEG4",
    "MSMPEG4V2",
    "MSMPEG4V3",
    "MSVIDEO1",
    "NELLYMOSER",
    "OPUS",
    "PAM",
    "PBM",
    "PCM_ALAW",
    "PCM_DVD",
    "PCM_F32BE",
    "PCM_F32LE",
    "PCM_F64BE",
    "PCM_F64LE",
    "PCM_MULAW",
    "PCM_S16BE",
    "PCM_S16BE_PLANAR",
    "PCM_S16LE",
    "PCM_S16LE_PLANAR",
    "PCM_S24BE",
    "PCM_S24DAUD",
    "PCM_S24LE",
    "PCM_S24LE_PLANAR",
    "PCM_S32BE",
    "PCM_S32LE",
    "PCM_S32LE_PLANAR",
    "PCM_S64BE",
    "PCM_S64LE",
    "PCM_S8",
    "PCM_S8_PLANAR",
    "PCM_U16BE",
    "PCM_U16LE",
    "PCM_U24BE",
    "PCM_U24LE",
    "PCM_U32BE",
    "PCM_U32LE",
    "PCM_U8",
    "PCM_VIDC",
    "PCX",
    "PGM",
    "PGMYUV",
    "PNG",
    "PPM",
    "PRORES",
    "PRORES_AW",
    "PRORES_KS",
    "QTRLE",
    "RAWVIDEO",
    "RA_144",
    "ROQ",
    "ROQ_DPCM",
    "S302M",
    "SBC",
    "SGI",
    "SONIC",
    "SONIC_LS",
    "SRT",
    "SSA",
    "SUBRIP",
    "SUNRAST",
    "TARGA",
    "TRUEHD",
    "TTA",
    "UTVIDEO",
    "VC2",
    "VORBIS",
    "WAVPACK",
    "WEBVTT",
    "WMAV1",
    "WMAV2",
    "WRAPPED_AVFRAME",
    "XBM",
    "XFACE",
    "XWD",
]


# codecs_with_comment = {"LAGS": ""}
# codecs_with_comment = {"PICK": ""}
codecs_with_comment = {"ZSTD": ""}
# svideoPaths = [("Baptiste.avi", 20)]
# codecs_with_comment = {"HFYU": ""}
# codecs_with_comment = {"LAGS": ""}
codecs_with_comment = {"PICK": "", "ZSTD": "", "HFYU": "", "LAGS": ""}


def loadVideo(videoPath, max_images, force_black_and_white=False):
    if not os.path.exists(videoPath):
        raise FileNotFoundError(f"[Errno 2] No such file or directory: '{videoPath}'")
    videoCapture = cv2.cv2_VideoCapture()
    retval = videoCapture.open(videoPath)
    if not retval:
        raise Exception(
            "Impossible d'ouvrire le fichier , verifiez que le codec est installe"
        )
    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    retval, image = videoCapture.read()
    color = numpy.sum(numpy.diff(image, axis=2)) > 0

    if not retval:
        raise Exception(
            "Impossible de decoder le fichier , verifiez que le codec est installe"
        )
    images = []
    i = 0
    while retval and i < max_images:
        if not color and len(image.shape) > 2:
            image = numpy.ascontiguousarray(image[:, :, 0])
        elif force_black_and_white:
            image = numpy.mean(image, axis=2).astype("uint8")
        # if i > 5:
        #    image = image[:-5, :-5]
        images.append(image)
        retval, image = videoCapture.read()
        i += 1
    del videoCapture
    return (images, fps)


def __main__():
    for videoPath in videoPaths:
        times = {}
        force_black_and_white = False
        if isinstance(videoPath, tuple):
            if len(videoPath) == 2:

                videoPath, max_images = videoPath
            elif len(videoPath) == 3:
                videoPath, max_images, force_black_and_white = videoPath
            else:
                raise Exception(
                    "videoPath must be a string or a tuple (videopath,max_images) or (videopath,max_images,force_black_white)"
                )
        else:
            max_images = math.inf
        print(videoPath, "------------------")
        images, fps = loadVideo(videoPath, max_images, force_black_and_white)
        shape = images[0].shape
        color = len(shape) > 2

        # Create directory for videos tests
        directory, name, _ = splitPath(videoPath)
        outDirectory = joinPath(directory, "test_video_codecs")
        if not os.path.exists(outDirectory):
            os.mkdir(outDirectory)

        newShape = images[0].shape
        size = (newShape[1], newShape[0])

        all_image_indexs = list(range(len(images)))
        test_indexs = {
            "forward": all_image_indexs,
            "reverse": list(reversed(all_image_indexs)),
            "random": numpy.random.randint(
                low=0, high=len(images), size=(len(images) // 10) + 1
            ),
        }

        for codec, comment in codecs_with_comment.items():

            print(f"{codec}")
            codec_is_losless = True

            if codec in ["png", "jpg", "bmp"]:

                serparatedImagesDirectory = joinPath(outDirectory, name + " " + codec)
                if not os.path.exists(serparatedImagesDirectory):
                    os.mkdir(serparatedImagesDirectory)
                totalDigits = len(str(len(images) - 1))
                toFormat = "{}.{:0>%d}" % totalDigits
                outPaths = []
                start_write = perf_counter()
                for i, image in enumerate(images):
                    outPath = joinPath(
                        serparatedImagesDirectory, toFormat.format(name, i), codec
                    )
                    cv2.imwrite(outPath, image)
                    outPaths.append(outPath)
                end_write = perf_counter()
                start_read = perf_counter()
                for outPath in outPaths:
                    cv2.imread(outPath)
                end_read = perf_counter()
                times[codec] = {
                    "write": (end_write - start_write) / len(images),
                    "read": (end_read - start_read) / len(images),
                }

            elif len(codec) == 4 and codec.isupper():

                # write --------------------

                if codec in codec_names:
                    outPath = joinPath(outDirectory, name + "." + codec, "pickle")
                else:
                    outPath = joinPath(outDirectory, name + "." + codec, "avi")

                videoWriter = cv2.VideoWriter()
                fourcc = cv2.VideoWriter_fourcc(*str(codec))
                videoWriter.open(outPath, fourcc, fps, size, color)

                start_write = perf_counter()
                for image in images:
                    videoWriter.write(image)
                end_write = perf_counter()
                del videoWriter
                times[codec] = {"write": (end_write - start_write) / len(images)}

                # read -------------------------

                # videoCapture = VideoCapture()
                videoCapture = cv2.VideoCapture()
                retval = videoCapture.open(outPath)
                if not retval:
                    if comment:
                        print(f"     {comment}")
                    print(
                        "     Impossible d'ouvrire le fichier avec le codec, verifiez que le codec est installe"
                    )
                    continue

                retval, image = videoCapture.read()
                if not retval:
                    if comment:
                        print(f"     {comment}")
                    print(
                        "     Impossible de decoder le fichier avec le codec, verifiez que le codec est installe"
                    )
                    continue
                for order, indexs in test_indexs.items():
                    videoCapture.set(
                        cv2.CAP_PROP_POS_FRAMES, 0
                    )  # ne samble pas marcher !
                    max_diff = 0

                    nb_test_images = len(indexs)
                    new_images = []
                    start_read = perf_counter()
                    last_index = -1
                    # print(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
                    for index in indexs:
                        if index != last_index + 1:
                            videoCapture.set(cv2.CAP_PROP_POS_FRAMES, index)
                        retval, image = videoCapture.read()
                        if not retval:
                            print(
                                f"     impossible de lire à partir de la frame {index} en {order}"
                            )
                            break

                        if not color and len(image.shape) > 2:
                            image = image[:, :, 0]
                        new_images.append(image)
                        last_index = index
                    end_read = perf_counter()

                    # stats -------------------------
                    max_diff = 0
                    sum_diff_abs = 0
                    for index, new_image in zip(indexs, new_images):
                        orginal_image = images[index]
                        if not numpy.all(orginal_image == new_image):
                            codec_is_losless = False
                            diff_abs = abs(orginal_image - new_image.astype("int16"))
                            sum_diff_abs += diff_abs.sum()
                            max_diff = max(diff_abs.max(), max_diff)
                            break

                    times[codec][f"read {order}"] = (
                        end_read - start_read
                    ) / nb_test_images

                del videoCapture
            elif codec.startswith("json"):
                # images = images[:1]
                outPath = joinPath(outDirectory, name, codec)
                shape = images[0].shape
                start_write = perf_counter()
                if codec.endswith("_diff_temporel"):
                    last_image = numpy.zeros(shape, dtype="uint8")
                    # diff_image = numpy.empty(shape, dtype="uint8")
                    encoder = serializejson.Encoder(
                        outPath, bytes_compression_threads=8
                    )
                    encoder.clear()
                    for image in images:
                        diff_image = image - last_image  # 0.237 ms per hit
                        # evit alocation mais fait planter serialize json qui detecte que meme objet a déjà été serializé
                        # numpy.subtract(image, last_image, out=diff_image)
                        encoder.append(
                            diff_image, close=False
                        )  # 959 avec close = False , # 1091 avec close = True
                        last_image = image
                    encoder.close()
                else:
                    serializejson.dump(
                        images, outPath, bytes_compression_diff_dtypes=("uint8",)
                    )  # ,bytes_compression = ("blosc_zstd",1),bytes_compression_threads=1)
                end_write = perf_counter()
                start_read = perf_counter()
                new_images = serializejson.load(outPath)  # 575 msec
                if codec == "json_diff_temporel":
                    last_image = numpy.zeros(images[0].shape, dtype="uint8")
                    for new_image in new_images:
                        new_image += last_image  # 0.193 msec by image
                        last_image = new_image
                end_read = perf_counter()
                max_diff = 0
                for image, new_image in zip(images, new_images):
                    if not numpy.all(image == new_image):
                        codec_is_losless = False

                times[codec] = {
                    "write": (end_write - start_write) / len(images),
                    "read": (end_read - start_read) / len(images),
                }

                """elif codec == "pickle":
                    outPath = joinPath(outDirectory, name, codec)
                    start_write = perf_counter()
                    outFile = open(outPath, "wb")
                    pickle.dump(images, outFile)
                    outFile.close()
                    end_write = perf_counter()
                    start_read = perf_counter()
                    outFile = open(outPath, "rb")
                    pickle.load(outFile)
                    outFile.close()
                    end_read = perf_counter()"""
            else:
                raise Exception("unknow codec")

            if codec_is_losless:
                print(f"     {lime}losless{no_color}")
            else:
                percent_pixels_error = (
                    sum_diff_abs * 100 / (images[0].size * len(images))
                )
                # diff_abs_by_image = sum_diff_abs / len(images)
                if max_diff == 1:
                    print(
                        f"     {orange}quasi losless (max diff {max_diff} for {percent_pixels_error} % of pixels){no_color}"
                    )
                else:
                    print(
                        f"     {red}NOT losless (max diff {max_diff} with  {percent_pixels_error} % of pixel error){no_color}"
                    )

            if comment:
                print(f"     {blue}{comment}{no_color}")
            for key, secondes in times[codec].items():
                print(f"     {secondes*1000:.3f} msec to {key} an image")


__main__()
