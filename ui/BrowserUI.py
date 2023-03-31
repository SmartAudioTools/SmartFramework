from PyQt5 import QtWidgets
from qtpy import QtCore, QtGui
from SmartFramework.ui.UrlUI import UrlUI
from SmartFramework.ui import exceptionDialog, CustomTitleBar
from SmartFramework.files import directory, joinPath
from PyQt5 import QtTest
from random import random
from time import perf_counter as clock
import __main__

try:
    from PyQt5.QtWebEngineWidgets import (
        QWebEngineView,
    )  # plante lors de l'ouverture de QtDesigner car demande à ce que ce soit importé avant création de QApplication, ce que je n'arrive pas à faire
    from PyQt5.QtWebEngineWidgets import QWebEngineProfile

    bugLoadingQWebEngineView = False
except:
    QWebEngineView = QtWidgets.QWidget
    bugLoadingQWebEngineView = True


def randomWait(minTime, maxTime):
    randTime = int(minTime + random() * (maxTime - minTime))
    QtTest.QTest.qWait(randTime)


class BrowserUI(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, **kwargs)
        if not bugLoadingQWebEngineView:
            mainFolder = directory(__main__.__file__)
            persistentStoragePath = joinPath(mainFolder, "QtWebEnginePersistentStorage")
            defaultProfile = QWebEngineProfile.defaultProfile()
            defaultProfile.setCachePath(
                persistentStoragePath
            )  # par Cache HTTP, par defaut  C:/Users/Baptiste/AppData/Local/pythonw/cache/QtWebEngine/Default
            defaultProfile.setPersistentStoragePath(
                persistentStoragePath
            )  # pour Cookies, par defaut C:/Users/Baptiste/AppData/Local/pythonw/QtWebEngine/Default
            # defaultProfile.setHttpCacheType(QWebEngineProfile.NoCache) # ne permet pas de sauvegarder login facebook..
            # print(defaultProfile.httpCacheMaximumSize())

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.pushButton = QtWidgets.QPushButton(self, text="<")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self, text=">")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.urlui = UrlUI(self)
        self.horizontalLayout.addWidget(self.urlui)
        self.horizontalLayout.setStretch(2, 2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.webEngineView = QWebEngineView(self)
        self.verticalLayout.addWidget(self.webEngineView)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.sending = True

        # Connexions
        if not bugLoadingQWebEngineView:
            self.setAttribute(
                QtCore.Qt.WA_DeleteOnClose
            )  # evite que le processus continu à vivre comme un zombie
            self.pushButton.clicked.connect(self.webEngineView.back)
            self.pushButton_2.clicked.connect(self.webEngineView.forward)
            self.urlui.url.connect(self.webEngineView.setUrl)
            self.webEngineView.urlChanged.connect(self.urlui.setUrl)
            self.webEngineView.loadFinished.connect(self._loadFinished)
            self.webEngineView.renderProcessTerminated.connect(
                self._renderProcessTerminated
            )
            QtWidgets.QApplication.instance().lastWindowClosed.connect(
                self.lastWindowClosed
            )

        # Graphics
        self.resize(571, 300)

    def lastWindowClosed(self):
        self._insist = False

    def runJavaScript(self, *args, **kArgs):
        self.webEngineView.page().runJavaScript(*args, **kArgs)

    def html(self):
        self._html = None
        self.webEngineView.page().toHtml(self._html_callback)
        while self._html is None:
            QtWidgets.QApplication.instance().processEvents()
        return self._html

    def _html_callback(self, html):
        self._html = html

    def javaScript(self, code):
        Flag = float("nan")
        self._javaScriptCallbackReturn = Flag
        self.webEngineView.page().runJavaScript(code, self._javaScript_callback)
        while self._javaScriptCallbackReturn is Flag:
            QtWidgets.QApplication.instance().processEvents()
        return self._javaScriptCallbackReturn

    def _javaScript_callback(self, value):
        self._javaScriptCallbackReturn = value

    def _renderProcessTerminated(self):
        print("renderProcessTerminated")

    @QtCore.Slot(str)
    def setUrl(self, url):
        print("setUrl ", url)
        self._loading = True
        if not bugLoadingQWebEngineView:
            self.webEngineView.setUrl(QtCore.QUrl(url))

    def getUrl(self):
        return self.webEngineView.url().toString()

    @QtCore.Slot(str)
    def load(self, url):
        """attention ce n'est pas bloquant !"""
        self._loading = True
        self.webEngineView.load(QtCore.QUrl(url))

    @QtCore.Slot(str)
    def get(self, url, tryLapsTime=10, insist=True):
        """wait load finished"""
        # print("get "+url)
        self._loading = True
        self._insist = insist
        lastTry = perf_counter()
        self.webEngineView.setUrl(QtCore.QUrl(url))
        while self._loading and self._insist:  # le self._insist permet de
            now = perf_counter()
            if now > lastTry + tryLapsTime:
                lastTry = now
                print("try again to load %s" % url)
                self.webEngineView.setUrl(QtCore.QUrl(url))
            QtWidgets.QApplication.instance().processEvents()
        # print("after setUrl" , url)

    def _loadFinished(self, succed):
        if succed:
            self._loading = False
        print("loadFinished :", succed)

    def mousseClic(self, x, y):
        recipient = self.webEngineView.focusProxy()
        position = QtCore.QPointF(x, y)
        event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonPress,
            position,
            QtCore.Qt.LeftButton,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier,
        )
        QtWidgets.QApplication.instance().postEvent(recipient, event)
        QtWidgets.QApplication.instance().processEvents()
        event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonRelease,
            position,
            QtCore.Qt.LeftButton,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier,
        )
        QtWidgets.QApplication.instance().postEvent(recipient, event)
        QtWidgets.QApplication.instance().processEvents()

    def sendKey(self, key, modifier=QtCore.Qt.NoModifier):
        if isinstance(key, int):
            intKey = key
            strKey = QtGui.QKeySequence(key).toString()
        elif isinstance(key, str):
            intKey = QtGui.QKeySequence.fromString(key)[0]
            strKey = key
        recipient = self.webEngineView.focusProxy()
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, intKey, modifier, strKey, False)
        QtWidgets.QApplication.instance().postEvent(recipient, event)
        QtWidgets.QApplication.instance().processEvents()
        event = QtGui.QKeyEvent(
            QtCore.QEvent.KeyRelease, intKey, modifier, strKey, False
        )
        QtWidgets.QApplication.instance().postEvent(recipient, event)
        QtWidgets.QApplication.instance().processEvents()

    def sendText(self, text, humanize=True):
        recipient = self.webEngineView.focusProxy()
        for strKey in text:
            if self.sending:
                if strKey == "\n":
                    strKey = "Enter"
                    intKey = QtCore.Qt.Key_Enter
                    modifier = QtCore.Qt.ControlModifier
                else:
                    intKey = QtGui.QKeySequence.fromString(strKey)[0]
                    modifier = QtCore.Qt.NoModifier
                event = QtGui.QKeyEvent(
                    QtCore.QEvent.KeyPress, intKey, modifier, strKey, False
                )
                QtWidgets.QApplication.instance().postEvent(recipient, event)
                QtWidgets.QApplication.instance().processEvents()
                if humanize:
                    randomWait(25, 50)
                event = QtGui.QKeyEvent(
                    QtCore.QEvent.KeyRelease, intKey, modifier, strKey, False
                )
                QtWidgets.QApplication.instance().postEvent(recipient, event)
                QtWidgets.QApplication.instance().processEvents()
                if humanize:
                    randomWait(25, 50)

    def removeText(self, length):
        for i in range(length):
            self.sendKey(QtCore.Qt.Key_Backspace)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = BrowserUI()
    widget.show()
    app.exec_()
