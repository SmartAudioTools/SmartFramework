import sys
from qtpy import QtGui, QtCore, QtWidgets, QtOpenGL, API

classes = []


class QOpenGLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, parent=None, **kwargs):
        QtWidgets.QOpenGLWidget.__init__(self, parent, **kwargs)
        format_ = QtGui.QSurfaceFormat()

        QtGui.QOpenGLPixelTransferOptions().setAlignment(1)
        QtGui.QOpenGLPixelTransferOptions().setAlignment(4)  #: ne marche pas
        format_.setSamples(4)
        self.setFormat(format_)

    def paintGL(self):

        # def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), self.palette().window())
        # painter.beginNativePainting()
        painter.setRenderHints(painter.Antialiasing | painter.TextAntialiasing)
        painter.drawText(QtCore.QPointF(10.1, 30.1), text)
        # painter.endNativePainting();
        painter.end()


classes.append(QOpenGLWidget)

if not API.endswith("6"):

    class QGLWidget(QtOpenGL.QGLWidget):
        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHints(painter.Antialiasing | painter.TextAntialiasing)
            painter.drawText(QtCore.QPointF(10.1, 30.1), text)
            painter.end()

    classes.append(QGLWidget)


class QWidget(QtWidgets.QWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(painter.Antialiasing | painter.TextAntialiasing)
        painter.drawText(QtCore.QPointF(10.1, 30.1), text)
        painter.end()


classes.append(QWidget)

text = "hello 01234"
app = QtWidgets.QApplication(sys.argv)
pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Window, QtCore.Qt.white)
Main = QtWidgets.QWidget()
Layout = QtWidgets.QGridLayout(Main)
for col, class_ in enumerate((QWidget, QOpenGLWidget)):
    widget = class_()
    widget.setPalette(pal)
    widget.setAutoFillBackground(True)
    Layout.addWidget(QtWidgets.QLabel(text=f"{class_.__name__}"), 0, col)
    Layout.addWidget(widget, 1, col)
Layout.setRowStretch(1, 3)
Main.resize(Main.width(), 150)
Main.show()
Main.setWindowTitle(API)
app.exec_()
