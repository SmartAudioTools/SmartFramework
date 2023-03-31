# https://stackoverflow.com/questions/18116650/is-it-possible-to-play-flac-files-in-phonon
# https://stackoverflow.com/questions/6951046/how-to-play-an-audiofile-with-pyaudio

from qtpy import QtCore, QtWidgets
import soundfile

# import pydub
import pyaudio
import wave
import numpy as np
from SmartFramework.audio.info import bitperfectDevices


pyaudio_format_from_subtype = dict(
    PCM_32=pyaudio.paInt32,
    PCM_24=pyaudio.paInt32,
    PCM_16=pyaudio.paInt16,
    FLOAT=pyaudio.paFloat32,
    PCM_U8=pyaudio.paUInt8,
    PCM_S8=pyaudio.paInt8,
    MPEG_LAYER_III=pyaudio.paInt16,
)

numpy_dtype_from_subtype = dict(
    PCM_32=np.int32,
    PCM_24=np.int32,
    PCM_16=np.int16,
    FLOAT=np.float32,  # probleme
    MPEG_LAYER_III=np.int16,
)


class AudioFilePlayer(QtCore.QObject):
    soundEnded = QtCore.Signal()
    soundLenght = QtCore.Signal(float)
    position = QtCore.Signal(float)
    playing = QtCore.Signal(bool)

    def __init__(
        self,
        parent=None,
        path=None,
        bufferSize=128,
        backend="soundfile",
        use_callback=False,
        **kargs,
    ):
        if isinstance(parent, QtCore.QThread):
            # ATTENTION il ne faut pas passer parent pour permet moveToThread
            QtCore.QObject.__init__(self, **kargs)
            self.moveToThread(parent)
        else:
            super(AudioFilePlayer, self).__init__(parent, **kargs)
        self.__dict__["bufferSize"] = bufferSize
        self.backend = backend
        self._playing = False
        self._stream = None
        self._audioFile = None
        self._device = None
        self._use_callback = use_callback
        self._pyaudio = None
        if path:
            self.setPathAndPlay(path)

    @QtCore.Slot(int)
    def setBufferSize(self, bufferSize):
        print("set bufferSize :", bufferSize)
        if self.__dict__["bufferSize"] != bufferSize:
            # pass
            # print(type(bufferSize))
            self.__dict__["bufferSize"] = bufferSize
            self._recreateStreamIfNeeded(force=True)

    @QtCore.Slot(str)
    def setDevice(self, device):
        if self._device != device:
            self._device = device
            self._recreateStreamIfNeeded(force=True)

    @QtCore.Slot(str)
    def setPathAndPlay(self, path):
        self.setPath(path)
        self.play()

    @QtCore.Slot(str)
    def setPath(self, path):
        audioFile = AudioFile(path, self.backend)
        if self._audioFile is not None:  # va poser pb avec callback ?
            old_audioFile = self._audioFile
            self._audioFile = audioFile
            old_audioFile.close()
        else:
            self._audioFile = audioFile
        self.soundLenght.emit(round(audioFile.lenght / audioFile.samplerate, 1))
        self._recreateStreamIfNeeded()

    @QtCore.Slot(float)
    def setPosition(self, position):
        if self._audioFile is not None:
            self._audioFile.setPosition(position)

    @QtCore.Slot(bool)
    def play(self, play=True):
        if play and self._audioFile is not None:
            self._playing = True
            self.playing.emit(True)
            if not self._use_callback:
                self._tick()
        else:
            self.pause()

    @QtCore.Slot()
    def pause(self):
        """self._led_timer.stop()"""
        self._playing = False
        self.playing.emit(False)

    def stop(self):
        self._playing = False
        self.playing.emit(False)
        self.position.emit(0.0)
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        if self._audioFile is not None:
            self._audioFile.close()

    @QtCore.Slot()
    def close(self):
        self.stop()
        if self._pyaudio is not None:
            self._pyaudio.terminate()

    def _recreateStreamIfNeeded(self, force=False):
        audioFile = self._audioFile
        if audioFile is not None:
            if self._pyaudio is None:
                self._pyaudio = pyaudio.PyAudio()
            if self._use_callback:
                callback = self._callback
            else:
                callback = None
            stream = self._stream
            if (
                force
                or stream is None
                or stream._format != audioFile.format
                or stream._channels != audioFile.channels
                or stream._rate != audioFile.samplerate
                or stream._frames_per_buffer != self.bufferSize
            ):
                if stream is not None:
                    stream.stop_stream()
                    stream.close()
                print(f"create stream with bufferSize {self.bufferSize}")
                self._stream = stream = self._pyaudio.open(
                    format=audioFile.format,
                    channels=audioFile.channels,
                    rate=audioFile.samplerate,
                    output=True,
                    output_device_index=bitperfectDevices[self._device],
                    stream_callback=callback,
                    # ça qui semble poser pb sur Lubuntu:
                    frames_per_buffer=self.bufferSize,
                )
                stream.start_stream()
                # pour eviter de planter avec ASIO4ALL :
                while stream.get_write_available() < 2 * self.bufferSize:
                    # print(stream.get_write_available())
                    pass

    @QtCore.Slot()
    def _tick(self):
        audioFile = self._audioFile
        if audioFile is not None and self._playing:
            # print(".", end = None)
            data = audioFile.read(self.bufferSize)  # retourn un numpy.arra
            if len(data):
                # la que ca a bloque au bout de quelqeus iterations quand met buffeur size
                self._stream.write(bytes(data.data))
                self.position.emit(audioFile.getPosition())
                QtCore.QTimer.singleShot(0, self._tick)
            elif self._playing:
                self._playing = False
                self.soundEnded.emit()

    @QtCore.Slot()
    def _callback(self, in_data, frame_count, time_info, status):
        audioFile = self._audioFile
        if audioFile is not None and self._playing:
            data = audioFile.read(frame_count)
            self.position.emit(audioFile.getPosition())
            return (data, pyaudio.paContinue)


class AudioFile:
    def __init__(self, path, backend):
        self.backend = backend

        if self.backend == "pydub":
            f = open(path, "rb")
            wf = pydub.AudioSegment.from_file(f)
            format_ = (pyaudio.get_format_from_width(wf.sample_width),)
            channels = wf.channels
            samplerate = wf.frame_rate

        elif self.backend == "wavfile":
            wf = wave.open(path, "rb")

        elif self.backend == "soundfile":
            wf = soundfile.SoundFile(path, "r")
            format_ = pyaudio_format_from_subtype[wf.subtype]
            channels = wf.channels
            samplerate = wf.samplerate

        self.path = path
        self.wf = wf
        self.format = format_
        self.channels = channels
        self.samplerate = samplerate
        self.dtype = numpy_dtype_from_subtype[wf.subtype]
        self.lenght = wf.frames
        self.sample_size = pyaudio.get_sample_size(format_)

    def getPosition(self):
        return self.wf.tell() / self.samplerate

    def setPosition(self, pos):
        self.wf.seek(int(pos * self.samplerate))

    def read(self, bufferSize):
        if self.backend == "pydub":
            pass
        elif self.backend == "soundfile":
            # return self.wf.buffer_read(bufferSize, dtype='int16')
            return self.wf.read(bufferSize, always_2d=True, dtype=self.dtype)

    def close(self):
        self.wf.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    audioFilePlayer = AudioFilePlayer(None)
    audioFilePlayer.setPathAndPlay(
        "D:/Ben Sharpa - Check The Evidence '08.flac"
    )  # "pcm1644s.wav")

    app.exec_()
    del widget
    del app
