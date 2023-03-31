# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 16:47:17 2014

@author: Baptiste
"""

from qtpy import QtGui, QtWidgets, QtCore
from qtpy.phonon import Phonon


class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.media = Phonon.MediaObject(self)
        self.media.stateChanged.connect(self.handleStateChanged)
        self.video = Phonon.VideoWidget(self)
        self.video.setMinimumSize(400, 400)
        self.audio = Phonon.AudioOutput(Phonon.VideoCategory, self)
        Phonon.createPath(self.media, self.audio)
        Phonon.createPath(self.media, self.video)
        self.button = QtWidgets.QPushButton("Choose File", self)
        self.button.clicked.connect(self.handleButton)
        self.list = QtWidgets.QListWidget(self)
        self.list.addItems(Phonon.BackendCapabilities.availableMimeTypes())
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.video, 1)
        layout.addWidget(self.button)
        layout.addWidget(self.list)

    def handleButton(self):
        if self.media.state() == Phonon.PlayingState:
            self.media.stop()
        else:
            path = QtWidgets.QFileDialog.getOpenFileName(self, self.button.text())
            if path:
                self.media.setCurrentSource(Phonon.MediaSource(path))
                self.media.play()

    def handleStateChanged(self, newstate, oldstate):
        if newstate == Phonon.PlayingState:
            self.button.setText("Stop")
        elif newstate != Phonon.LoadingState and newstate != Phonon.BufferingState:
            self.button.setText("Choose File")
            if newstate == Phonon.ErrorState:
                source = self.media.currentSource().fileName()
                print(("ERROR: could not play:", source.toLocal8Bit().data()))
                print(("  %s" % self.media.errorString().toLocal8Bit().data()))


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Phonon Player")
    window = Window()
    window.show()
    sys.exit(app.exec_())
