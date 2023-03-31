from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.syncObjectUI import SyncObjectUI

codecs = ["Menu", "DIB ", "LAGS"]  # 'ASLC','FFV1','HFYU','LZO1','PIMJ','ZLIB'


class VideoCodecMenuUI(SyncObjectUI):
    outCodec = QtCore.Signal(str)

    def __init__(self, parent=None):
        # appel constructeur de la Classe de base :
        SyncObjectUI.__init__(self, parent, syncName="videoCodec")
        # connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable:
        self.outCodec.connect(self._sync.input)
        # connection à l'attribut sync herité de SyncOBject  => permet de rendre l'objet synchronisable:
        self._sync.output[str].connect(self.setCodec)

        self.comBox = QtWidgets.QComboBox(self)
        self.comBox.addItems(codecs)
        self.comBox.setCurrentIndex(-1)
        self.comBox.currentTextChanged.connect(self.outCodec)

    def __getstate__(self):
        if self.serialize:
            return {"Codec": self.Codec}

    # properties
    @QtCore.Slot(str)
    def setCodec(self, name):
        index = self.comBox.findText(name)
        if index != -1:
            self.comBox.setCurrentIndex(index)

    def getCodec(self):
        return self.comBox.currentText()

    Codec = QtCore.Property(str, getCodec, setCodec)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoCodecMenuUI()
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
