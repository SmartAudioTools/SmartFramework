# -*- coding: utf-8 -*-
import logging
import sys
from qtpy import QtCore, QtGui, QtWidgets


logger = logging.getLogger(__name__)


class StdErrUI(QtWidgets.QTextBrowser):
    def __init__(self, parent=None):
        super(StdErrUI, self).__init__(parent)
        # create connections
        XStream.stderr().messageWritten.connect(self.insertPlainText)
        # XStream.stderr().messageWritten.connect( self.insertPlainText )
        #        print(QtWidgets.QApplication.instance().topLevelWidgets())


class XStream(QtCore.QObject):
    _stderr = None
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
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr

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
    widget = StdErrUI()
    widget.show()
    sys.exit(app.exec_())
