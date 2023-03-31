# -*- coding: utf-8 -*-
import logging
import sys
from qtpy import QtCore, QtGui, QtWidgets


logger = logging.getLogger(__name__)


class StdOutUI(QtWidgets.QTextBrowser):
    def __init__(self, parent=None):
        super(StdOutUI, self).__init__(parent)
        # create connections
        XStream.stdout().messageWritten.connect(self.insertPlainText)
        # XStream.stderr().messageWritten.connect( self.insertPlainText )
        #        print(QtWidgets.QApplication.instance().topLevelWidgets())


class XStream(QtCore.QObject):
    _stdout = None
    # _stderr = None

    messageWritten = QtCore.Signal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    """
    @staticmethod
    def stderr():
        if ( not XStream._stderr ):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr
        """


if __name__ == "__main__":

    logging.basicConfig()
    app = QtWidgets.QApplication(sys.argv)
    widget = StdOutUI()
    widget.show()
    sys.exit(app.exec_())
