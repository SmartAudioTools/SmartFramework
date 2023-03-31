from qtpy import QtGui, QtCore, QtWidgets


class CustomTitleBar(QtWidgets.QWidget):
    """
    http://doc.qt.io/qt-5/qdockwidget.html#setTitleBarWidget
    #_ZNK22QDockWidgetTitleButton8sizeHintEv:
    https://code.woboq.org/qt5/qtbase/src/widgets/widgets/qdockwidget.cpp.html
    """

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

    def docked(self):
        QDockWidget = self.parent()
        if QDockWidget.isFloating():
            return False
        else:
            try:
                return bool(QDockWidget.parent().tabifiedDockWidgets(QDockWidget))
            except:
                return True

    def sizeHint(self):
        # self.ensurePolished()

        # size = 2*self.style().pixelMetric(QtWidgets.QStyle.PM_DockWidgetTitleBarButtonMargin, None, self)
        # if not self.icon().isNull :
        #    sz = self.icon().actualSize(self.dockButtonIconSize());
        #    size += max(sz.width(), sz.height())
        if self.docked():
            size = 10
        else:
            size = QtGui.QFontMetrics(self.font()).height()
        return QtCore.QSize(size, size)

    def minimumSizeHint(self):
        return self.sizeHint()

    """def event(self,event):
        if event.type() == QtCore.QEvent.MouseMove :
             event.ignore()
             return False
        return QtWidgets.QWidget.event(self,event)"""

    def paintEvent(self, event):
        if not self.docked():
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            rect = event.rect()
            text = self.parent().windowTitle()
            alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
            opt = QtWidgets.QStyleOption()
            opt.initFrom(self)
            fm = QtGui.QFontMetrics(self.font())
            if True:
                halfHeight = 0.5 * (rect.height())
                drawColor = QtGui.QColor(255, 255, 255, 255)
                pen = QtGui.QPen(drawColor)
                penWidth = 2
                pen.setWidthF(penWidth)
                painter.setPen(pen)
                roundedRect = QtCore.QRectF(rect).adjusted(
                    penWidth / 2, halfHeight, -penWidth / 2, 10
                )
                painter.drawRoundedRect(roundedRect, 10, 10)
                textBackgroundRect = self.style().itemTextRect(
                    fm, rect, alignment, self.isEnabled(), text
                )
                path = QtGui.QPainterPath()
                path.addRect(QtCore.QRectF(textBackgroundRect.adjusted(-10, 0, 10, 0)))
                painter.fillPath(path, QtGui.QColor(0, 0, 0, 255))
            self.style().drawItemText(
                painter,
                rect,
                alignment,
                opt.palette,
                self.isEnabled(),
                text,
                self.foregroundRole(),
            )
        else:
            painter = QtGui.QPainter(self)
            rect = event.rect()
            drawColor = QtGui.QColor(255, 255, 255, 255)
            pen = QtGui.QPen(drawColor)
            penWidth = 2
            pen.setWidthF(penWidth)
            painter.setPen(pen)
            roundedRect = QtCore.QRectF(rect).adjusted(
                penWidth / 2, penWidth / 2, -penWidth / 2, 30
            )
            painter.drawRoundedRect(roundedRect, 10, 10)
