# -*- coding: utf-8 -*-
from qtpy import QtCore, QtWidgets
from SmartFramework.video.ObjectsRecord import ObjectsRecord
from SmartFramework.video.VideoWriter import VideoWriter


KiloOctet = 1024
MegaOctet = 1024**2


class VideoRecord(ObjectsRecord):

    """PyQt class for video recording"""

    # constructor ------------

    def __init__(
        self,
        parent=None,
        path=None,
        codec="ZSTD",
        extension="zstd",
        fps=75,
        useBuffer=False,
        askBeforReplace=True,
        speak=False,
        addDate=False,
        checkMemoryPeriode=75,
        ramSecuritySpace=1000 * MegaOctet,
        discSecuritySpace=MegaOctet,
    ):
        """path is None "%s %s.avi"%(mainName,strftime('%Y-%m-%d_%HH%M_%S', localtime())) will be uses"""
        super(VideoRecord, self).__init__(
            parent=parent,
            path=path,
            extension=extension,
            useBuffer=useBuffer,
            askBeforReplace=askBeforReplace,
            speak=speak,
            addDate=addDate,
            checkMemoryPeriode=checkMemoryPeriode,
            ramSecuritySpace=ramSecuritySpace,
            discSecuritySpace=discSecuritySpace,
        )
        self._tags = None
        self.codec = codec
        self.fps = fps

    # slot / (futur) properties Qt------

    @QtCore.Slot(object)
    def setTags(self, tags):
        self.__dict__["tags"] = tags

    @QtCore.Slot(int)
    @QtCore.Slot(float)
    def setFps(self, value):
        self.__dict__[
            "fps"
        ] = value  # utilise cette syntaxe pour ne pas faire de boucle infini quand créera propriété QT dans ma compilation poru Qt Designer

    @QtCore.Slot(str)
    def setCodec(self, value):
        self.__dict__["codec"] = value

    # reimplementation methodes de ObjectsRecord ------------------

    def objectRamSize(self, obj):
        return obj.nbytes + 48

    def objectDiscSize(self, obj):
        return obj.nbytes + 48

    def openWriter(self, path, objExemple):
        return VideoWriter(path, self.codec, self.fps, self.tags)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoRecord()
    app.exec_()
