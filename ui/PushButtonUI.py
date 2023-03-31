from qtpy import QtCore, QtGui, QtWidgets
from SmartFramework.sync.syncObjectUI import Sync


class PushButtonUI(QtWidgets.QPushButton):
    def __init__(
        self,
        parent=None,
        value=False,
        repeat=True,
        syncModule="synced",
        syncName="",
        syncSave=True,
        serialize=True,
        **kwargs
    ):
        QtWidgets.QPushButton.__init__(self, parent, **kwargs)

        # synchronisation & serialization
        self._sync = Sync(self, syncModule=syncModule, syncName=syncName, save=syncSave)
        self.toggled.connect(self._sync.input)
        self._sync.output[bool].connect(self.setValue)
        self._serialize = serialize

        self._repeat = repeat
        self.setValue(value)
        # self.setAlignment(alignment)

    # slot / property

    @QtCore.Slot(int)
    @QtCore.Slot(bool)
    def setValue(self, b):
        b = bool(b)
        if b == self.isChecked() and self._repeat:
            self.toggled.emit(b)
        else:
            self.setChecked(bool(b))

    value = QtCore.Property(bool, QtWidgets.QPushButton.isChecked, setValue)

    @QtCore.Slot(str)
    def setText(self, text):
        QtWidgets.QPushButton.setText(self, text)

    # events

    def mousePressEvent(self, event):
        QtWidgets.QPushButton.click(self)

    def mouseReleaseEvent(self, event):
        pass

    # synchro et serialisation
    def setSyncModule(self, value):
        self._sync.syncModule = value

    def getSyncModule(self):
        return self._sync.syncModule

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        self._sync.syncName = value
        # print('setSyncName : ' + value)

    def getSyncName(self):
        return self._sync.syncName

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        self._sync.save = value

    def getSyncSave(self):
        return self._sync.save

    syncSave = QtCore.Property(bool, getSyncSave, setSyncSave)

    """
    def setAlignment(self,alignment):
        # alignement horizontal 
        self._alignment = alignment
        if alignment &  QtCore.Qt.AlignLeft :
            self.setStyleSheet("Text-align:left")            
        elif alignment &  QtCore.Qt.AlignRight :
            self.setStyleSheet("Text-align:right")        
        elif alignment &  QtCore.Qt.AlignHCenter:
            self.setStyleSheet("Text-align:center")   
    def getAlignment(self):
        return QtCore.Qt.Alignment(self._alignment) N'ARRIVE PAS A RETOURNER CE QU'IL FAUT POUR QUE QT DESIGNER RECUPER LA BONNE VALEURE !!!!!!
        #if self._alignment == QtCore.Qt.AlignRight:
        #    return QtCore.Qt.AlignLeft #self._alignment
        #if self._alignment == QtCore.Qt.AlignLeft:
        #    return QtCore.Qt.AlignLeft #self._alignment
        #if self._alignment == QtCore.Qt.AlignHCenter:
        #    return QtCore.Qt.AlignHCenter #self._alignment
        
    alignment = QtCore.Property(QtCore.Qt.Alignment, getAlignment, setAlignment)
    """

    # serialization

    def setSerialize(self, value):
        self._serialize = value

    def getSerialize(self):
        return self._serialize

    serialize = QtCore.Property(bool, getSerialize, setSerialize)

    def __getstate__(self):
        if self._serialize:
            return {"value": self.value}


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = PushButtonUI(text="coucou")
    widget.show()
    app.exec_()
