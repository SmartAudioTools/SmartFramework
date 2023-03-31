# -------- Audio Data -------------------
class AudioEvt:
    def __init__(self, sampling):
        pass
        # self.data       =       # numpy, liste, str, dict
        # self.samplingRate
        # self.channel          # liste de vues sur rawArray si entrelace , tableau bruts sinon ...
        # self.entrelace
        # self.size
        # self.nbChannels
        # self.timestamp
        # self.type          # plutot self.data.dtype ?
        # self.representation  # PCM, FFT, WAVELET


class AudioData:
    def getBlocks():
        pass

    def getNextBlock():
        pass


def convert(objetIn, typeIn, TypeOut):
    pass
    # str -> numpy
    # numpy -> str
    # numpyInt -> numpyFloat
    # numptFloat -> nympyInt (dithering)


class MP3:
    def __init__(self, fileName):

        # ouverture du fichier et lecture d'un bout de fichier

        self.fileName = fileName
        self.extension = str.split(fileName, ".")[-1].lower()  # recupère extension

        # ouverture d'un fichier WAV
        if self.extension == "wav":
            f = wave.open(fileName, "rb")
            data = f.readframes()
            self.sampleRate = f.getframerate()
            self.channels = f.getnchannels()
            self.format = sound.AFMT_S16_LE

        # ouverture d'un fichier MP3 , WMA , etc...
        else:

            # initialisation -------

            f = open(self.fileName, "rb")
            header = f.read(
                32000
            )  # lit un morceau du fichier sufisament grand pou avoir au moin une frame et recuperer infos

            # decoupe en frames et recupere TAG

            import pymedia.muxer as muxer

            demuxer = muxer.Demuxer(
                self.extension
            )  # initialise le demuxer (permet de sperarer les differents types de données contenus dans 1 frame)
            frames = demuxer.parse(
                header
            )  # analyse le morceau de fichier,le decoupe en retournant une liste de frames et créer le tuple dm.streams , chaque frame correspond à une liste [0,données , longeure ,0L,0L]
            print(demuxer.hasHeader(), demuxer.getHeaderInfo())  # info Tag

            # decode 1ere frame et recupère paramètres Audio
            import pymedia.audio.acodec as acodec

            decoder = acodec.Decoder(
                demuxer.streams[0]
            )  # initalise le decodeur (permet de decompresser les données .data contenus dans une 1 frame)  (dm.streams[0] est crée lors du premier dm.parse(s))

            r = decoder.decode(frames[0][1])
            r.bitrate
            self.channels = r.channels
            self.format = r.sample_length
            self.sampleRate = r.sample_rate

            # boucle de lecture ----------

            f.seek(
                0
            )  # retourne au debut du fichier pour pouvoir lire normalement par la suite sans avoir eu a stocker les premieres frames qu'on avait utilisé pour recuperer infos
            demuxer.reset()  # reset le buffeur du demultiplexeur
            s = " "
            listeStrData = []
            while len(s):
                s = f.read(32000)
                if len(s):
                    frames = demuxer.parse(s)
                    for frame in frames:
                        r = decoder.decode(frame[1])
                        if r and r.data:
                            listeStrData.append(r.data)
            # self.listeStrData = listeStrData

            # transformation de liste de string en tableau numpy du type de l'entrée.

            listNumpyData = []
            for strData in listeStrData:
                listNumpyData.append(numpy.frombuffer(strData, dtype="int16"))
            self.data = numpy.concatenate(listNumpyData)
