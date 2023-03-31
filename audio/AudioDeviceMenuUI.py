from qtpy import QtCore, QtWidgets
from SmartFramework.ui.ControlUI import ControlUI
from SmartFramework.audio.info import bitperfectDevices


class AudioDeviceMenuUI(ControlUI):
    hideBufferSizeSelector = QtCore.Signal(bool)

    def __init__(self, parent=None, autoHide=True):
        ControlUI.__init__(self, parent)
        self.audioDevices = list(bitperfectDevices.keys())
        self.autoHide = autoHide
        self.setItems(self.audioDevices)

    def setLastAudioDevices(self, lastAudioDevices):
        if self.autoHide and set(lastAudioDevices) == set(self.audioDevices):
            self.hide()
            self.hideBufferSizeSelector.emit(True)

    def __getstate__(self):
        return {
            "value": self._items[int(self.value)],
            "lastAudioDevices": self.audioDevices,
        }


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = AudioDeviceMenuUI()
    widget.show()  # si objet avec Interface graphique (UI)
    app.exec_()
