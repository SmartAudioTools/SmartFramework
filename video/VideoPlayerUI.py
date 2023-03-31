from qtpy import QtCore, QtGui, QtWidgets, API_NAME, scaled
from SmartFramework.files.FileDialog import FileDialog
from SmartFramework.ui.FlonumUI import FlonumUI
from SmartFramework.ui.IntSliderUI import IntSliderUI
from SmartFramework.video.VideoPlayer import VideoPlayer
from qtpy.QtCore import QSettings
from SmartFramework.ui import exceptionDialog, CustomTitleBar


class VideoPlayerUI(QtWidgets.QWidget):

    # constructor

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, **kwargs)

        self.videoplayer = VideoPlayer(self)
        self.filedialog = FileDialog(
            self, title="Open Movie", filter="Movie Files (*.avi)"
        )
        self.intsliderui = IntSliderUI(self)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self._horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self._horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_4 = QtWidgets.QPushButton(
            self.horizontalLayoutWidget, text="open"
        )
        self._horizontalLayout.addWidget(self.pushButton_4)
        self.lineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self._horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(
            self.horizontalLayoutWidget, text="play"
        )
        self._horizontalLayout.addWidget(self.pushButton)
        self.pushButton_6 = QtWidgets.QPushButton(
            self.horizontalLayoutWidget, text="pause"
        )
        self._horizontalLayout.addWidget(self.pushButton_6)
        self.pushButton_2 = QtWidgets.QPushButton(
            self.horizontalLayoutWidget, text="stop"
        )
        self._horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_5 = QtWidgets.QPushButton(
            self.horizontalLayoutWidget, text="prev"
        )
        self._horizontalLayout.addWidget(self.pushButton_5)
        self.pushButton_3 = QtWidgets.QPushButton(
            self.horizontalLayoutWidget, text="next"
        )
        self._horizontalLayout.addWidget(self.pushButton_3)
        self.flonumui = FlonumUI(self, minimum=-10.0, maximum=10.0, value=1.0)

        # Connexions
        self.filedialog.outputFileName[str].connect(self.lineEdit.setText)
        self.filedialog.selectPath[str].connect(self.videoplayer.setPath)
        self.flonumui.valueChanged[float].connect(self.videoplayer.setSpeed)
        self.intsliderui.valueChanged[int].connect(self.videoplayer.inFrameNumber)
        self.pushButton.clicked.connect(self.videoplayer.play)
        self.pushButton_2.clicked.connect(self.videoplayer.stop)
        self.pushButton_3.clicked.connect(self.videoplayer.next)
        self.pushButton_4.clicked.connect(self.filedialog.open)
        self.pushButton_5.clicked.connect(self.videoplayer.prev)
        self.pushButton_6.clicked.connect(self.videoplayer.pause)
        self.videoplayer.outFrameCountLessOne[int].connect(self.intsliderui.setMaximum)
        self.videoplayer.outFrameNumber[int].connect(self.intsliderui.setValue)
        self.videoplayer.outImage[object].connect(self.outImage[object])

        # Graphics
        self.resize(1365, 84)
        self.intsliderui.setGeometry(scaled(QtCore.QRect(0, 50, 1361, 31)))
        self.horizontalLayoutWidget.setGeometry(scaled(QtCore.QRect(-10, 0, 1311, 48)))
        self.flonumui.setGeometry(scaled(QtCore.QRect(1310, 10, 50, 46)))

    # signals

    outImage = QtCore.Signal(object)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = VideoPlayerUI()
    widget.setWindowTitle(f"{Widget} ({{API_NAME}})")
    widget.show()
    app.exec_()
    del widget
    del app
