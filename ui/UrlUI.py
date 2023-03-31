from qtpy import QtCore, QtWidgets


class UrlUI(QtWidgets.QLineEdit):
    url = QtCore.Signal(QtCore.QUrl)

    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.returnPressed.connect(self.emitUrl)

    def emitUrl(self):
        self.url.emit(QtCore.QUrl(self.text()))

    def setUrl(self, url):
        if isinstance(url, QtCore.QUrl):
            url = url.toString()
        if isinstance(url, str) and url != self.text():
            self.setText(url)
            # self.url.emit(QtCore.QUrl(url))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = LineEditUI()
    widget.show()
    app.exec_()
