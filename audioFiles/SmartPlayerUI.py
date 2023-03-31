from qtpy import QtCore, QtGui, QtWidgets, API_NAME, scaled
from SmartFramework.Thread import Thread
from SmartFramework.audio.AudioDeviceMenuUI import AudioDeviceMenuUI
from SmartFramework.audioFiles.AudioFilePlayer import AudioFilePlayer
from SmartFramework.files.FileDialogUI import FileDialogUI
from SmartFramework.serialize.SerializeInterface import SerializeInterface
from SmartFramework.ui.ControlUI import ControlUI
from qtpy.QtCore import QSettings
from SmartFramework.ui import exceptionDialog, CustomTitleBar


class SmartPlayerUI(QtWidgets.QWidget):
    # constructor

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, **kwargs)

        self._gridLayout = QtWidgets.QGridLayout(self)
        self._gridLayout.setContentsMargins(*scaled(0, 0, 0, 0))
        self._gridLayout.setSpacing(0)

        self._commandWidget = QtWidgets.QWidget(self)
        self._gridLayout2 = QtWidgets.QGridLayout(self._commandWidget)
        self._gridLayout2.setContentsMargins(*scaled(10, 10, 10, 10))
        self._gridLayout2.setSpacing(scaled(10))

        self._play = ControlUI(self, text="►", checkable=True)
        self._gridLayout2.addWidget(self._play, 1, 0, 1, 1)
        self.audiodevicemenuui = AudioDeviceMenuUI(self)
        self.audiodevicemenuui.setAlignment(QtCore.Qt.AlignCenter)

        self._gridLayout2.addWidget(self.audiodevicemenuui, 0, 0, 1, 1)
        self._next = ControlUI(self, text="►►")
        self._gridLayout2.addWidget(self._next, 1, 2, 1, 1)
        self.filedialogui = FileDialogUI(self, ext="*.flac,*.mp3,*.wav,*.ogg,*.wma")
        self._gridLayout.addWidget(self.filedialogui, 0, 0, 1, 1)
        self._position = ControlUI(self, isTime=True)
        self._gridLayout2.addWidget(self._position, 1, 1, 1, 1)

        self._gridLayout.addWidget(self._commandWidget, 1, 0, 1, 1)
        self.buffersize = ControlUI(
            self,
            value=3.0,
            maximum=5.0,
            prefix="Buffer size :",
            itemsDictStr='{"16":16,"32":32,"64":64,"128":128,"512":512,"1024":1024}',
        )
        self._gridLayout2.addWidget(self.buffersize, 0, 1, 1, 1)
        self.serializeinterface = SerializeInterface(self, target="self.parent()")
        self.thread = Thread(self)
        self._audiofileplayer = AudioFilePlayer(self)  # self.thread)
        self._gridLayout.setRowStretch(0, 1)
        self.audiodevicemenuui.setPrefix("Device :")

        # Connexions
        self._audiofileplayer.playing[bool].connect(self._play.setValueWithoutEmit)
        self._audiofileplayer.position[float].connect(
            self._position.setValueWithoutEmit
        )
        self._audiofileplayer.soundLenght[float].connect(self._position.setMaximum)
        self._audiofileplayer.soundEnded.connect(self.filedialogui.selectNext)
        self._next.pressed.connect(self.filedialogui.selectNext)
        self._play.toggled[bool].connect(self._audiofileplayer.play)
        self._position.valueChanged[float].connect(self._audiofileplayer.setPosition)
        self.audiodevicemenuui.valueChanged[str].connect(
            self._audiofileplayer.setDevice
        )
        self.buffersize.valueChanged[int].connect(self._audiofileplayer.setBufferSize)
        self.filedialogui.currentPath[str].connect(self._audiofileplayer.setPathAndPlay)
        self.audiodevicemenuui.hideBufferSizeSelector.connect(self.buffersize.setHidden)

        # Graphics
        self.resize(500, 700)


if __name__ == "__main__":
    import sys, os

    app = QtWidgets.QApplication(sys.argv)
    app.setDesktopFileName("SmartPlayer")
    widget = SmartPlayerUI()
    widget.setWindowTitle("SmartPlayer")
    iconPath = os.path.dirname(__file__) + "/SmartPlayer.ico"
    widget.setWindowIcon(QtGui.QIcon(iconPath))
    widget.show()
    widget.window().activateWindow()
    app.exec_()
    del widget
    del app
