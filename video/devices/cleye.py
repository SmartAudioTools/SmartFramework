# -*- coding: utf-8 -*-
# biding pour CLEyeMulticam.dll


import numpy as np
from numpy.ctypeslib import ndpointer
import ctypes
from ctypes.wintypes import BYTE, WORD, DWORD
from time import perf_counter
import os

# DEFINITION DES TYPES POUR CTYPES -----------------------------------------------


class GUID(ctypes.Structure):
    _fields_ = [("Data1", DWORD), ("Data2", WORD), ("Data3", WORD), ("Data4", BYTE * 8)]


# API C de CLEye -------------------------------------------------------------

thisfilepath = os.path.dirname(os.path.abspath(__file__))
dll_name = thisfilepath + "/CLEyeMulticam.dll"
# print( dll_name)
import __main__

if hasattr(__main__, "__file__"):  # pour eviter de planter QtDesigner
    dll = ctypes.cdll.LoadLibrary(str(dll_name))

    # camera instance
    ##typedef void *CLEyeCameraInstance;

    # Camera information
    ## int  CLEyeGetCameraCount();
    ## GUID CLEyeGetCameraUUID(int camId);
    dll.CLEyeGetCameraUUID.argtypes = [ctypes.c_int]  # camId
    dll.CLEyeGetCameraUUID.restype = GUID

    # Library initialization
    ## CLEyeCameraInstance CLEyeCreateCamera(GUID camUUID, CLEyeCameraColorMode mode, CLEyeCameraResolution res, int frameRate);
    dll.CLEyeCreateCamera.argtypes = [
        GUID,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_float,
    ]  # camUUID, CLEyeCameraColorMode mode, CLEyeCameraResolution res, float frameRate
    dll.CLEyeCreateCamera.restype = ctypes.c_void_p
    ## bool CLEyeDestroyCamera(CLEyeCameraInstance cam);

    # Camera capture control
    ## bool CLEyeCameraStart(CLEyeCameraInstance cam);
    ## bool CLEyeCameraStop(CLEyeCameraInstance cam);

    # Camera settings control
    ## bool CLEyeSetCameraParameter(CLEyeCameraInstance cam, CLEyeCameraParameter param, int val);
    ## int  CLEyeGetCameraParameter(CLEyeCameraInstance cam, CLEyeCameraParameter param);

    # Camera video frame image data retrieval
    ## bool CLEyeCameraGetFrameDimensions(CLEyeCameraInstance cam, int &width, int &height);
    ## bool CLEyeCameraGetFrame(CLEyeCameraInstance cam, PBYTE pData, int waitTimeout = 2000);
    dll.CLEyeCameraGetFrame.argtypes = [
        ctypes.c_void_p,
        ndpointer(dtype=np.uint8, flags=("C_CONTIGUOUS", "WRITEABLE")),
        ctypes.c_int,
    ]  # cam, ptr, timeout

    # Camera LED control
    ## bool CLEyeCameraLED(CLEyeCameraInstance cam, bool on);
    dll.CLEyeCameraLED.argtypes = [ctypes.c_void_p, ctypes.c_bool]


# CONSTANTES -------------------------------------------------------------------

# camera modes (CLEyeCameraColorMode)
CLEYE_MONO_PROCESSED = 0  # 8 bit per pixel grayscale image
CLEYE_COLOR_PROCESSED = (
    1  # 32bit per pixel : 8 bit read => RGBX (little-endian), 32bit read => 0x00RRGGBB
)
CLEYE_MONO_RAW = 2
CLEYE_COLOR_RAW = 3
CLEYE_BAYER_RAW = 4
cleyeMode = {
    "MONO_PROCESSED ": 0,
    "COLOR_PROCESSED": 1,
    "MONO": 2,
    "COLOR": 3,
    "BAYER": 4,
}

# camera resolution (CLEyeCameraResolution)
# CLEYE_QVGA = 0        # 320x240 image resolurion, Allowed frame rates: 15, 30, 60, 75, 100, 125
# VCLEYE_GA  = 1        # 640x480 image resolution, Allowed frame rates: 15, 30, 40, 50, 60, 75
cleyeResolution = {"QVGA": 0, "VGA": 1}


# camera parameters (CLEyeCameraParameter)
# camera sensor parameters
(
    CLEYE_AUTO_GAIN,  # [false, true]
    CLEYE_GAIN,  # [0, 79]
    CLEYE_AUTO_EXPOSURE,  # [false, true]
    CLEYE_EXPOSURE,  # [0, 511]
    CLEYE_AUTO_WHITEBALANCE,  # [false, true]
    CLEYE_WHITEBALANCE_RED,  # [0, 255]
    CLEYE_WHITEBALANCE_GREEN,  # [0, 255]
    CLEYE_WHITEBALANCE_BLUE,  # [0, 255]
    # camera linear transform parameters (valid for CLEYE_MONO_PROCESSED, CLEYE_COLOR_PROCESSED modes)
    # ( ne les ai pas bindé car a priori traitement aprés reception. (a verifier) )
    CLEYE_HFLIP,  # [false, true] # Flip video horizontally.
    CLEYE_VFLIP,  # [false, true]
    CLEYE_HKEYSTONE,  # [-500, 500]
    CLEYE_VKEYSTONE,  # [-500, 500]
    CLEYE_XOFFSET,  # [-500, 500]
    CLEYE_YOFFSET,  # [-500, 500]
    CLEYE_ROTATION,  # [-500, 500]
    CLEYE_ZOOM,  # [-500, 500]
    # camera non-linear transform parameters (valid for CLEYE_MONO_PROCESSED, CLEYE_COLOR_PROCESSED modes)
    # ( ne les ai pas bindé car a priori traitement aprés reception. (a verifier))
    CLEYE_LENSCORRECTION1,  # [-500, 500]
    CLEYE_LENSCORRECTION2,  # [-500, 500]
    CLEYE_LENSCORRECTION3,  # [-500, 500]
    CLEYE_LENSBRIGHTNESS,  # [-500, 500]
) = list(range(20))


def calculComposantes(frame):
    A = frame[::2, ::2]
    B = frame[1::2, ::2]
    C = frame[::2, 1::2]
    D = frame[1::2, 1::2]

    print("A : %f" % A.sum())
    print("B : %f" % B.sum())
    print("C : %f" % C.sum())
    print("D : %f" % D.sum())


# FONCTIONS ------------------------------------------------------------------


def cameraCount():
    return dll.CLEyeGetCameraCount()


def cameraUUID(i):
    """The unique camera UUID. This represents the unique identifier for a given
    camera that stays with that camera no matter if it gets plugged in to
    another USB port or another system. This allows allows developers to
    uniquely track cameras by saving the camera UUID values in their application
    configuration file. This value can be retrieved by calling
    CLEyeGetCameraUUID function."""
    return dll.CLEyeGetCameraUUID(i)


# OBJECT ---------------------------------------------------------------------


class VideoCapture(object):
    # def __init__(self, device = 0,fps = 190.0, mode = 'MONO', resolution = 'QVGA', paddingChannel = True, autoGain = False, autoExposure = False, autoWhiteBalance = False, gain = 40,exposure = 512,whiteBalance = (122,132,127),led = True, rotation = 2):
    def __init__(
        self,
        device=0,
        fps=75.0,
        mode="BAYER",
        resolution="VGA",
        paddingChannel=True,
        autoGain=False,
        autoExposure=False,
        autoWhiteBalance=False,
        gain=0,
        exposure=512,
        whiteBalance=[122, 129, 127],
        led=True,
        rotation=2,
        autostart=True,
    ):

        self.__dict__.update(locals())
        self._guid = dll.CLEyeGetCameraUUID(device)
        self._cleyeMode = cleyeMode[mode]
        self._cam = None
        self._mustRestart = False
        if autostart:
            self.start()

    def read(self, timeout=1000):

        if self._cam:
            if self._mustRestart:
                self.stop()
                self.start()
            if not self.led:
                dll.CLEyeCameraLED(
                    self._cam, False
                )  # on est obligé d'eteindre regulièrement la LED , sinon se ralume parfois toute seule...BUG DE Code Laboratories

            if (
                self._cleyeMode == CLEYE_COLOR_PROCESSED
                or self._cleyeMode == CLEYE_COLOR_RAW
            ):
                frame = np.empty((self._width, self._height, 4), np.uint8)
                frameOk = dll.CLEyeCameraGetFrame(self._cam, frame, timeout)
                if frameOk:
                    # print(frame.take([3],axis=2))
                    if not self.paddingChannel:
                        frame = frame.take([0, 1, 2], axis=2)
                    return np.rot90(frame, self.rotation)
                else:
                    return None
            else:
                frame = np.empty((self._width, self._height), np.uint8)
                frameOk = dll.CLEyeCameraGetFrame(self._cam, frame, timeout)
                if frameOk:
                    if self.rotation:
                        return np.rot90(
                            frame, self.rotation
                        )  # 0.0059 msec sur macbook   "return A rotated view of m .", par contre defer  a par contre défère le traitement à np.ascontiguousarray  qui lui prend 0.176 msec sur macbook pro et 0.743 msec sur pipo !
                    else:
                        return frame
                else:
                    return None
        else:
            return None

    def start(
        self,
    ):  # n'existe pas dans l'API cv2.VideoCapture, rajouté ici pour permetre de changer dynamiquement fps etc...
        print("start cam !!!!")  # , oiu
        self._mustRestart = False
        self._cam = dll.CLEyeCreateCamera(
            self._guid,
            self._cleyeMode,
            cleyeResolution[self.resolution],
            float(self.fps),
        )
        if self.resolution == "QVGA":
            self._height, self._width = 320, 240
        else:
            self._height, self._width = 640, 480

        # remet les parametres (meme si on a pas reussi à demarer la cam , permet au moins de les stocker)
        self.setGain(self.gain)
        self.setExposure(self.exposure)
        self.setWhiteBalance(self.whiteBalance)
        self.setAutoExposure(self.autoExposure)
        self.setAutoWhiteBalance(self.autoWhiteBalance)
        # dll.CLEyeSetCameraParameter(self._cam,CLEYE_HFLIP, True)
        # demare la camera
        self.setAutoGain(self.autoGain)
        dll.CLEyeCameraStart(self._cam)
        self.setLed(
            self.led
        )  # vire le bug d'affichage en permetant temporisation  pendant changement de résoltuion !?

    def stop(
        self,
    ):  # n'existe pas dans l'API cv2.VideoCapture, rajouté ici pour permetre de changer dynamiquement fps etc...
        print("stop cam")
        dll.CLEyeCameraStop(self._cam)
        dll.CLEyeDestroyCamera(self._cam)
        self._cam = None

    def __del__(self):
        # print('del')
        dll.CLEyeCameraStop(self._cam)
        dll.CLEyeDestroyCamera(self._cam)

    def setRotation(self, value):
        self.rotation = value

    # peuvent à présent être modifié à chaud

    def setDevice(self, device):
        if self.device != device:
            self.device = device
            self._guid = dll.CLEyeGetCameraUUID(self.device)
            self._mustRestart = True

    def setMode(self, mode):
        # print(mode)
        if self.mode != mode:
            self.mode = mode
            self._cleyeMode = cleyeMode[mode]
            self._mustRestart = True

    def setResolution(self, resolution):

        if resolution and self.resolution != resolution:
            print("setResolution :: ", resolution)  # , UIO
            self.resolution = resolution
            self._mustRestart = True

    def setFps(self, fps):
        if self.fps != fps:
            self.fps = fps
            self._mustRestart = True

    # camera sensor parameters, peuvent etre modifiés à chaud

    def setAutoGain(self, value):
        self.autoGain = value
        if self._cam:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_AUTO_GAIN, value)
        self.setGain(self.gain)

    def setGain(self, value):
        self.gain = value
        if self._cam and not self.autoGain:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_GAIN, value)

    def setAutoExposure(self, value):
        self.autoExposure = value
        if self._cam:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_AUTO_EXPOSURE, value)
        self.setExposure(self.exposure)

    def setExposure(self, value):
        self.exposure = value
        if self._cam and not self.autoExposure:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_EXPOSURE, value)

    def setAutoWhiteBalance(self, value):
        self.autoWhiteBalance = value
        if self._cam:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_AUTO_WHITEBALANCE, value)
        self.setWhiteBalance(self.whiteBalance)

    def setWhiteBalance(self, rgb):
        self.whiteBalance = rgb
        r, g, b = rgb
        if self._cam and not self.autoWhiteBalance:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_WHITEBALANCE_RED, r)
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_WHITEBALANCE_GREEN, g)
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_WHITEBALANCE_BLUE, b)

    def setWhiteBalanceR(self, r):
        self.whiteBalance[0] = r
        if self._cam and not self.autoWhiteBalance:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_WHITEBALANCE_RED, r)

    def setWhiteBalanceG(self, g):
        self.whiteBalance[1] = g
        if self._cam and not self.autoWhiteBalance:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_WHITEBALANCE_GREEN, g)

    def setWhiteBalanceB(self, b):
        self.whiteBalance[2] = b
        if self._cam and not self.autoWhiteBalance:
            dll.CLEyeSetCameraParameter(self._cam, CLEYE_WHITEBALANCE_BLUE, b)

    def setLed(self, value):
        # deconne un peu .......
        self.led = value
        if self._cam:
            dll.CLEyeCameraLED(self._cam, value)


if __name__ == "__main__":
    import cv2
    from time import sleep

    print("ESC : quiter")
    print("----")
    print("UP  : increase")
    print("DOWN: decrease")
    print("A   : auto On/Off")
    print("----")
    print("G   : gain")
    print("E   : exposure")
    print("W   : WhiteBalance")
    print("R   : rouge")
    print("V   : vert")
    print("B   : Bleu")
    print("m   : mode color/mono/bayer")
    print("S   : size VGA/QVGA")
    print("----")
    print("I   : print Infos")
    print("D   : change device")
    print("L   : LED on/off")
    print("P   : take a picture")
    print("N   : new name for picture")

    print("------ START ----------------")

    filePrefixe = None
    a = 0.03
    t_last = None
    smothInterval = None
    fps = 0

    dev = VideoCapture()

    cv2.namedWindow("camera", 1)
    parametre = None
    while True:
        frame = dev.read()
        if frame is not None:

            #
            t = perf_counter()

            if t_last:
                interval = t - t_last
                t_last = t
                if smothInterval:
                    smothInterval = interval * a + smothInterval * (1.0 - a)
                else:
                    smothInterval = interval
                newfps = round(1.0 / smothInterval)
                if abs(fps - newfps) > 2:
                    fps = newfps
                    # print("fps : %i" % fps)
            else:
                t_last = t

            cv2.imshow("camera", np.copy(frame))
            # cv2.imshow("camera", np.repeat(np.repeat((frame-128)*2,3,0),3,1))

            # cv2.imshow("camera", np.repeat(np.repeat(frame *5,3,0),3,1))
        else:
            pass
            print("pas de frame")
        ch = cv2.waitKey(1)

        # Traitement des touches clavier --------------------------------

        if ch >= 0 and ch < 256 and chr(ch) in "gewrvbfmt":
            parametre = chr(ch)

        if ch == ord("a"):
            if parametre == "g":
                autoGain = not dev.autoGain
                dev.setAutoGain(autoGain)
                print("autoGain : " + str(autoGain))
            if parametre == "e":
                autoExposure = not dev.autoExposure
                dev.setAutoExposure(autoExposure)
                print("autoExposure : " + str(autoExposure))
            if parametre == "w":
                autoWhiteBalance = not dev.autoWhiteBalance
                dev.setAutoWhiteBalance(autoWhiteBalance)
                print("autoWhiteBalance : " + str(autoWhiteBalance))

        if ch == ord("i"):
            print("--------------------")
            print("device :" + str(dev.device))
            from pybase64 import b64encode

            print("camera UUID :" + str(b64encode(dev._guid.__reduce__()[1][1][1])))
            print("color :" + str(dev.mode))
            print("fps :" + str(dev.fps))
            print("size :" + str(dev._width) + "," + str(dev._height))

            print("autoGain : " + str(dev.autoGain))
            print("autoExposure : " + str(dev.autoExposure))
            print("autoWhiteBalance : " + str(dev.autoWhiteBalance))

            print("Gain : " + str(dev.gain))
            print("Exposure : " + str(dev.exposure))
            print("WhiteBalance : " + str(dev.whiteBalance))

            print("composante RGB")
            calculComposantes(frame)

            print("maximum : %i , minimum : %i" % (np.max(frame), np.min(frame)))
        if ch == ord("d"):
            dev.setDevice(not dev.device)

        if ch == ord("s"):
            if dev.resolution == "VGA":
                dev.setResolution("QVGA")
            else:
                dev.setResolution("VGA")

        if ch == ord("l"):
            dev.setLed(not dev.led)

        if ch == 27:
            break

        if ch == 2490368:
            if parametre == "m":
                intMode = dev.cleyeMode + 1
                mode = [k for k, v in cleyeMode.items() if v == intMode][0]
                dev.setMode(mode)
            if parametre == "f":
                fps = dev.fps + 1
                dev.setFps(fps)
                print("Fps : " + str(fps))
            if parametre == "g":
                dev.setGain(dev.gain + 1)
            if parametre == "e":
                dev.setExposure(dev.exposure + 1)
            if parametre == "r":
                r, g, b = dev.whiteBalance
                dev.setWhiteBalance(r + 1, g, b)
            if parametre == "v":
                r, g, b = dev.whiteBalance
                dev.setWhiteBalance(r, g + 1, b)
            if parametre == "b":
                r, g, b = dev.whiteBalance
                dev.setWhiteBalance(r, g, b + 1)
            if parametre == "t":
                dev.setRotation(dev.rotation + 1)
        if ch == ord("n"):
            filePrefixe = input("File prefixe : ")
        if ch == ord("p"):
            import time

            if filePrefixe == None:
                filePrefixe = input("File prefixe : ")
            fileName = (
                filePrefixe
                + ",color="
                + str(dev.mode)
                + ",fps="
                + str(dev.fps)
                + ",Gain="
                + str(dev.gain)
                + ",Exposure="
                + str(dev.exposure)
                + ",WhiteBalance="
                + str(dev.whiteBalance)
            )
            filePath = "D:/" + fileName + time.asctime().replace(":", "_") + ".png"
            print(filePath)
            # print(frame.size)
            cv2.imwrite(filePath, np.copy(frame))
        if ch == 2621440:
            if parametre == "m":
                intMode = dev.cleyeMode - 1
                mode = [k for k, v in cleyeMode.items() if v == intMode][0]
                dev.setMode(mode)
            if parametre == "f":
                fps = dev.fps - 1
                dev.setFps(fps)
                print("Fps : " + str(fps))
            if parametre == "g":
                dev.setGain(dev.gain - 1)
            if parametre == "e":
                dev.setExposure(dev.exposure - 1)
            if parametre == "r":
                r, g, b = dev.whiteBalance
                dev.setWhiteBalance(r - 1, g, b)
            if parametre == "v":
                r, g, b = dev.whiteBalance
                dev.setWhiteBalance(r, g - 1, b)
            if parametre == "b":
                r, g, b = dev.whiteBalance
                dev.setWhiteBalance(r, g, b - 1)
            if parametre == "t":
                dev.setRotation(dev.rotation - 1)

    dev.stop()
    cv2.destroyWindow("camera")
