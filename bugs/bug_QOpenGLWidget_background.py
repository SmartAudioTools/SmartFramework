import sys
from qtpy import QtGui, QtCore, QtWidgets, QtOpenGL, API

classes = [QtWidgets.QWidget]


class QWidget_paintEvent(QtWidgets.QWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.end()


classes.append(QWidget_paintEvent)

if not API.endswith("6"):
    classes.append(QtOpenGL.QGLWidget)

    class QGLWidget_paintEvent(QtOpenGL.QGLWidget):
        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.end()

    classes.append(QGLWidget_paintEvent)

classes.append(QtWidgets.QOpenGLWidget)


class QOpenGLWidget_paintEvent(QtWidgets.QOpenGLWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.end()


classes.append(QOpenGLWidget_paintEvent)


class QOpenGLWidget_paintEvent_with_fillRect(QtWidgets.QOpenGLWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), self.palette().window())
        painter.end()


classes.append(QOpenGLWidget_paintEvent_with_fillRect)

app = QtWidgets.QApplication(sys.argv)
pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Window, QtCore.Qt.green)


# show
Main = QtWidgets.QWidget()
Layout = QtWidgets.QGridLayout(Main)
for col, class_ in enumerate(classes):
    widget = class_()
    # widget.resize(100, 100)
    widget.setPalette(pal)
    widget.setAutoFillBackground(True)
    Layout.addWidget(QtWidgets.QLabel(text=f"{class_.__name__}"), 0, col)
    Layout.addWidget(widget, 1, col)
Layout.setRowStretch(1, 3)
# Main.resize(2 * width * window_scale, 2 * heigt * window_scale)
Main.resize(Main.width(), 200)
Main.show()
app.exec_()
