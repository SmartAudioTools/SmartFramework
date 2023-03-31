# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 11:39:54 2018

@author: Baptiste
"""
from qtpy import QtCore
from gtts import gTTS
from SmartFramework.audio.playsound import playsound
from SmartFramework.string import toValidPath
from SmartFramework.files import joinPath

# from SmartFramework.string.guess_language import guess_language
from SmartFramework.string.languageDetector import languageDetector
import os


class Speech(QtCore.QObject):
    def __init__(self, parent=None, mp3Folder="speech"):
        super(Speech, self).__init__(parent)
        self.mp3Folder = mp3Folder
        self._languageDetector = languageDetector()
        if not os.path.isdir(mp3Folder):
            os.mkdir(mp3Folder)

    def toMp3(self, text, lang=None, path=None):
        if lang is None:
            lang = self._languageDetector.detect(text)
        tts = gTTS(text=text, lang=lang)
        if path is None:
            path = self.getPath(text)
        tts.save(path)
        return path

    def getPath(self, text):
        name = toValidPath(text)
        path = joinPath(self.mp3Folder, name, "mp3")
        return path

    @QtCore.Slot(str)
    def speech(self, text, lang=None, block=False):
        if text:
            path = self.getPath(text)
            if not os.path.exists(path):
                self.toMp3(text, lang=lang, path=path)
            playsound(path, block=block)


if __name__ == "__main__":
    phrases = ["This library is free software ok", "stop", "bonjour les amis"]
    speech = Speech()
    for phrase in phrases:
        speech.speech(phrase, block=True)
