from qtpy import QtCore, QtGui, QtWidgets
from time import perf_counter
import cv2


class VideoRecord(QtCore.QObject):
    """par defaut recFps si pas présisé sera calé sur inFps au moment de debut de l'enregistrement
    recFps ne change plus aprés le début de l'enregistrement"""

    # constructor ------------

    def __init__(
        self, parent=None, path="./videorec.avi", codec="DIB ", inFps=190, recFps=None
    ):
        super(VideoRecord, self).__init__(parent)
        self.path = path
        self.codec = codec
        self.recFps = recFps
        self.inFps = inFps
        self._running = False

        # parametres pour calcul du inFpsCalculate

        self.a = 0.03
        self.t_last = None
        self.smothInterval = None
        self.inFpsCalculate = None

    # signaux ------------

    outRecTime = QtCore.Signal(float)

    # slots ------------

    @QtCore.Slot()
    def start(self):
        if self.path and not self._running:
            self._first = True
            self._running = True

    @QtCore.Slot()
    def stop(self):
        if self._running:
            del self.videoWriter
            self._running = False

    @QtCore.Slot(bool)
    def startStop(self, b):
        if b:
            self.start()
        else:
            self.stop()

    @QtCore.Slot(object)
    def inImage(self, img):
        t = perf_counter()
        if not self.inFps:
            # calcule du inFpsCalculate
            if self.t_last:
                interval = t - self.t_last
                if self.smothInterval:
                    self.smothInterval = interval * self.a + self.smothInterval * (
                        1.0 - self.a
                    )
                else:
                    self.smothInterval = interval
                self.inFpsCalculate = 1.0 / self.smothInterval

        # detection de frame skiping ?

        if self._running:
            if self._first:

                if self.recFps:
                    self.recordingFps = self.recFps
                elif self.inFps:
                    self.recordingFps = self.inFps
                else:
                    self.recordingFps = round(
                        self.inFpsCalculate
                    )  # on choisit un framerate entier.... pas forcement le mieux , mais bon ....

                if self.recordingFps:
                    # self.inFpsCalculate n'a peut être pas encore de valeure
                    print(("recording FPS : %f" % self.recordingFps))
                    self._first = False
                    self.inAvance = 0.0
                    self.videoWriter = cv2.VideoWriter()
                    shape = img.shape
                    size = (shape[1], shape[0])
                    retval = self.videoWriter.open(
                        self.path,
                        cv2.VideoWriter_fourcc(*self.codec),
                        self.recordingFps,
                        size,
                    )
                    if not retval:
                        if codec == "LAGS" and cv2.__version__ > "3.4.3":
                            raise Exception(
                                "Open CV ne supporte plus le codec LAGS en ecriture après la version 3.4.3"
                            )
                        raise Exception(
                            "Impossible d'ouvrire le fichier video %s en ecriture , verifiez que le codec est installe"
                            % self.recPath
                        )

            if self.inFps:
                # print("on a un inFps théorique")
                # on choisit la webcam comme source de temps (il ne vaut pas de skiping ...)
                # permet de calculer temps webcam théorique ( on permet aussi un variation de inFps théorique)

                if self.inFps == self.recordingFps:
                    self.videoWriter.write(img)

                else:
                    self.inAvance += 1.0 / self.inFps
                    while 0 < self.inAvance:
                        self.inAvance -= 1.0 / self.recordingFps
                        self.videoWriter.write(img)
            else:
                # print("on a pas de inFPs théorique ...")
                # on choisit la webcam comme source de temps uniqument si le inFpsCalculé n'a pas changé depuis le debut de l'enregistremetn

                if round(self.inFpsCalculate) == self.recordingFps:
                    self.videoWriter.write(img)

                else:
                    # pour mesurer temps ,  on prefère le mesure avec perf_counter()
                    # on risque d'avoir des frame repetée et d'autres skipée. => il faudra gerer ca .....
                    self.inAvance += t - self.t_last  # permet variation du fps d'entrée
                    frameDiff = 0
                    while 0 < self.inAvance:
                        self.inAvance -= 1.0 / self.recordingFps
                        self.videoWriter.write(img)
                        frameDiff += 1
                    if frameDiff < 1:
                        print("frame skipped")
                    if frameDiff > 1:
                        print("frame reppet x %d" % frameDiff)

            # self.outRecTime.emit(self.recFrame/self.recordingFps)
        self.t_last = t

    # slot / (futur) properties ------

    @QtCore.Slot(float)
    def setInFps(self, value):
        self.__dict__[
            "inFps"
        ] = value  # utilise cette syntaxe pour ne pas faire de boucle infini quand créera propriété QT dans ma compilation poru Qt Designer

    @QtCore.Slot(float)
    def setRecFps(self, value):
        self.__dict__["recFps"] = value

    @QtCore.Slot(str)
    def setPath(self, value):
        self.__dict__["path"] = value

    @QtCore.Slot(str)
    def setCodec(self, value):
        self.__dict__["codec"] = value


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoRecord()
    app.exec_()
