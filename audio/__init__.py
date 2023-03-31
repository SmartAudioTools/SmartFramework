# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pyaudio
import numpy
from qtpy import QtCore, QtGui, uic
from .data import *
from .in_out import *
import os.path


# ------------------- Audio ---------------------------------


class AudioThread(QtCore.QThread):  #
    def __init__(self, audioFile, parametres):
        QtCore.QThread.__init__(self)
        self.audioFile = audioFile
        self.parametres = parametres
        self.start(self.HighestPriority)

    def run(self):
        if self.audioFile:
            self.audio = loadFile(self.audioFile, self.parametres)
        # self.audio.solution_while()
        self.exec_()


class Audio(QtCore.QObject):

    # ------ start/stop -----------------------------------------------"

    def __init__(
        self,
        parametres=None,
        BLOCKSIZE=512,
        CHANNELS=2,
        SAMPLERATE=44100,
        INPUT=True,
        OUTPUT=True,
        DEVICE=0,
        METHODE="solution_signaux",
    ):

        QtCore.QObject.__init__(self)
        self.timer = QtCore.QTimer()
        self.mutex = QtCore.QMutex()

        # Recupere parametre par defaut
        # 128      # taille des block pour appel bloquants (ATTENTION ! pas forcement egale a FRAME_PER_BUFFER!) #16 parait bien si frame_pre_buffer pas multiple de fireface:
        self.BLOCKSIZE = BLOCKSIZE
        self.CHANNELS = CHANNELS
        self.SAMPLERATE = SAMPLERATE
        self.INPUT = INPUT
        self.OUTPUT = OUTPUT
        self.DEVICE = DEVICE
        self.METHODE = METHODE

        # tente de recuper parametre du fichier de parametre
        self.BLOCKSIZE = (
            parametres.BLOCKSIZE
        )  # 128      # taille des block pour appel bloquants (ATTENTION ! pas forcement egale a FRAME_PER_BUFFER!) #16 parait bien si frame_pre_buffer pas multiple de fireface
        self.CHANNELS = parametres.CHANNELS
        self.SAMPLERATE = parametres.SAMPLERATE
        self.INPUT = parametres.INPUT
        self.OUTPUT = parametres.OUTPUT
        self.DEVICE = parametres.DEVICE
        self.METHODE = parametres.METHODE

        # autres Constantes
        self.FRAMES_PER_BUFFER = self.BLOCKSIZE
        self.BLOCKTIME = self.BLOCKSIZE / 44.100

        # attributs d'etat
        self.p = pyaudio.PyAudio()
        self.running = 0
        self.streamOpen = 0
        self.blockCounter = 0
        self.vol = 1

        # ouverture du stream
        try:
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.CHANNELS,
                rate=self.SAMPLERATE,
                input=self.INPUT,
                output=self.OUTPUT,
                input_device_index=self.DEVICE,
                output_device_index=self.DEVICE,
                frames_per_buffer=self.FRAMES_PER_BUFFER,
            )
            self.streamOpen = 1
            # self.start_stop(1)
        except IOError:
            print("impossible d'ouvrire le stream Audio")

    def start_stop(self, on_off):
        print("start")
        if on_off:
            if self.streamOpen == 1:
                self.running = 1
                if self.METHODE == "solution_timer_inteligent":
                    self.timer.singleShot(0, self.solution_timer_inteligent)
                elif self.METHODE == "solution_timer_0":
                    self.timer.singleShot(0, self.solution_timer_0)
                elif self.METHODE == "solution_timer_1":
                    self.timer.singleShot(0, self.solution_timer_1)
                elif self.METHODE == "solution_timer_blocktime":
                    self.timer.singleShot(0, self.solution_timer_blocktime)
                elif self.METHODE == "solution_signaux":
                    print("lance solution signaux")
                    self.timer.singleShot(0, self.solution_signaux)
        else:
            self.running = 0

    def close(self):
        self.running = 0  # self.stimer.stop() ne suffit pas a arreter timer.singleshot
        # self.wait()
        if self.streamOpen == 1:
            try:
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
            except IOError:
                print("impossible de fermer le stream Audio")

    # ------ Infos -----------------------------------------------

    def info_latency(self):
        print("------ INFO -----------------------------------------------")
        print("BLOCKTIME", self.BLOCKTIME)
        if self.INPUT:
            self.input_latency = self.stream.get_input_latency()
            print(
                "input latency en msec", int(self.input_latency * 1000.0 + 0.5), "msec"
            )
        if self.OUTPUT:
            self.output_latency = self.stream.get_output_latency()
            print(
                "output latency en msec",
                int(self.output_latency * 1000.0 + 0.5),
                "msec",
            )
        if self.INPUT & self.OUTPUT:
            print(
                "totale latency en msec",
                int(
                    (self.input_latency + self.output_latency) * 1000.0 + 0.5,
                ),
                "msec",
            )

    # ------Approche signaux -----------------------------------------------"
    def solution_signaux(self):
        if self.running:
            self.readAudio()

    def readAudio(self):
        if self.INPUT and self.running:
            # audioEvt = AudioEvt()
            try:
                inputString = self.stream.read(self.BLOCKSIZE)
            except IOError:
                inputString = self.BLOCKSIZE * self.CHANNELS * "0" * 4
            # le converti en numpy.array
            audioEvt = numpy.frombuffer(inputString, dtype="float32")

            self.emit(QtCore.SIGNAL("audioOutput"), audioEvt)
        # print("read")
        # return audioEvt

    def writeAudio(self, audioEvt):
        if self.OUTPUT:
            try:
                self.stream.write(audioEvt.tostring())
            except IOError:
                pass
        # self.emit(QtCore.SIGNAL('audioProcessed'))
        # print("write")
        if self.running:
            self.timer.singleShot(0, self.readAudio)

    # ------Datas -----------------------------------------------"

    def readBytes(self, size):
        if self.INPUT:
            try:
                inputBytes = self.stream.read(size)
            except IOError:
                inputBytes = size * self.CHANNELS * "0" * 4
        return inputBytes

    def writeBytes(self, outputBytes):
        if self.OUTPUT:
            try:
                self.stream.write(outputBytes)
            except IOError:
                pass

    def readArray(self, size):
        inputString = self.readBytes(size)  # le read retourn un chaine de caracteres
        # le converti en numpy.array
        return numpy.frombuffer(inputString, dtype="float32")

    def writeArray(self, outputArray):
        # Shove contents of buffer out audio port
        self.writeBytes(outputArray.tostring())

    def readChannels(self, size):
        inputArray = self.readArray(size)
        inputChannel = list(range(self.CHANNELS))
        for channel in range(self.CHANNELS):
            inputChannel[channel] = inputArray[channel :: self.CHANNELS]
        return inputChannel

    def writeChannels(self, outputChannel):
        outputArray = numpy.zeros(self.CHANNELS * self.BLOCKSIZE, dtype="float32")
        for channel in range(self.CHANNELS):
            outputArray[channel :: self.CHANNELS] = outputChannel[channel]
        self.writeArray(outputArray)
        # self.writeArray(outputChannel)

    #  Traitement Audio -----------------------------------

    def processArray(self, inArray):
        # self.vol = app.widget.spinBox.value() * 0.02 # approche sans connect
        self.mutex.lock()
        vol = self.vol
        self.mutex.unlock()
        outArray = inArray * vol
        return outArray

    def processChannels(self, inChannel):
        # self.vol = app.widget.spinBox.value() * 0.02 # approche sans connect
        self.mutex.lock()
        vol = self.vol
        self.mutex.unlock()
        inChannel[0] *= vol
        # for array in inChannel:
        #    array *= vol
        return inChannel

    def read_process_write(self):
        dataIn = self.readArray(self.BLOCKSIZE)
        dataOut = self.processArray(dataIn)
        self.writeArray(dataOut)

    # Solution de gestion Audio -----------------------------------

    def solution_timer_0(self):
        if self.running:
            self.read_process_write()
            self.timer.singleShot(0, self.solution_timer_0)

    def solution_timer_1(self):
        if self.running:
            # print("running")
            if self.stream.get_read_available() >= self.BLOCKSIZE:
                self.read_process_write()
            self.timer.singleShot(1, self.solution_timer_1)

    def solution_timer_blocktime(self):
        if self.running:
            self.read_process_write()
            self.timer.singleShot(
                max(0, int(self.BLOCKTIME) - 1), self.solution_timer_blocktime
            )

    def solution_timer_inteligent(self):
        if self.BLOCKSIZE < 1024:
            print("taille des block < 1024 => mode bloquant")
            self.solution_timer_0()
        else:
            print("taille des block >= 1024 => mode non-bloquant")
            self.solution_timer_1()
