from qtpy import QtCore, QtGui, QtWidgets, API_NAME, scaled
from SmartFramework.ui.ControlUI import ControlUI
from SmartFramework.video.Webcam import Webcam
from SmartFramework.video.WebcamMenuUI import WebcamMenuUI
from qtpy.QtCore import QSettings
from SmartFramework.ui import exceptionDialog, CustomTitleBar

Webcam = type("Webcam", (QtWidgets.QWidget,), dict(Webcam.__dict__))


class WebcamUI(Webcam):

    # constructor

    def __init__(self, parent=None, **kwargs):
        Webcam.__init__(self, parent, **kwargs)

        self._verticalLayout = QtWidgets.QVBoxLayout(self, spacing=scaled(10))
        self._verticalLayout.setContentsMargins(0, 0, 0, 0)
        self._webcamMenu = WebcamMenuUI(self)
        self._verticalLayout.addWidget(self._webcamMenu)
        self.widget = QtWidgets.QWidget(self)
        self._gridLayout = QtWidgets.QGridLayout(self.widget, spacing=scaled(10))
        self._gridLayout.setContentsMargins(0, 0, 0, 0)
        self._resolutionMenu = ControlUI(
            self.widget, items=["VGA", "QVGA"], sendInitValue=False
        )
        self._gridLayout.addWidget(self._resolutionMenu, 0, 0, 1, 1)
        self._modeMenu = ControlUI(
            self.widget, items=["BAYER", "MONO", "COLOR"], sendInitValue=False
        )
        self._gridLayout.addWidget(self._modeMenu, 0, 1, 1, 1)
        self._ledButton = ControlUI(
            self.widget, text="Leds", checkable=True, sendInitValue=False
        )
        self._gridLayout.addWidget(self._ledButton, 0, 2, 1, 1)
        self._fpsNumberUI = ControlUI(
            self.widget,
            value=0.0,
            minimum=0.0,
            maximum=200.0,
            singleStep=5.0,
            prefix="Fps ",
            sendInitValue=False,
            syncSave=False,
        )
        self._gridLayout.addWidget(self._fpsNumberUI, 1, 0, 1, 1)
        self._gainNumberUI = ControlUI(
            self.widget,
            value=0.0,
            maximum=512.0,
            prefix="Gain ",
            sendInitValue=False,
            syncSave=False,
        )
        self._gridLayout.addWidget(self._gainNumberUI, 1, 1, 1, 1)
        self._exposureNumberUI = ControlUI(
            self.widget,
            value=0.0,
            maximum=512.0,
            prefix="Expo ",
            sendInitValue=False,
            mouseSensibility=0.5,
            syncSave=False,
        )
        self._gridLayout.addWidget(self._exposureNumberUI, 1, 2, 1, 1)
        self._verticalLayout.addWidget(self.widget)
        self._verticalLayout.setStretch(0, 1)
        self._verticalLayout.setStretch(1, 2)

        # Connexions
        self.outDevice[str].connect(self._webcamMenu.setValueWithoutEmit)
        self.outEnableSettings[bool].connect(self.widget.setVisible)
        self.outExposure[int].connect(self._exposureNumberUI.setValueWithoutEmit)
        self.outFps[int].connect(self._fpsNumberUI.setValueWithoutEmit)
        self.outGain[int].connect(self._gainNumberUI.setValueWithoutEmit)
        self.outLed[bool].connect(self._ledButton.setValueWithoutEmit)
        self.outMode[str].connect(self._modeMenu.setValueWithoutEmit)
        self.outResolution[str].connect(self._resolutionMenu.setValueWithoutEmit)
        self._exposureNumberUI.valueChanged[int].connect(self.setExposure)
        self._fpsNumberUI.valueChanged[int].connect(self.setFps)
        self._gainNumberUI.valueChanged[int].connect(self.setGain)
        self._ledButton.valueChanged[bool].connect(self.setLed)
        self._modeMenu.textActivated[str].connect(self.setMode)
        self._resolutionMenu.valueChanged[str].connect(self.setResolution)
        self._webcamMenu.valueChanged[str].connect(self.setDevice)

        # Graphics
        self.resize(394, 190)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = WebcamUI()
    widget.setWindowTitle(f"Webcam ({API_NAME})")
    widget.show()
    app.exec_()
    del widget
    del app