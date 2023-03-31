from qtpy import QtCore, QtGui, QtWidgets
import pyHook


class GlobalMouse(QtCore.QObject):
    # objet en premier pour etre par defaut
    Position = QtCore.Signal((int, int,), (object,))
    PositionX = QtCore.Signal(int)
    PositionY = QtCore.Signal(int)
    WheelSens = QtCore.Signal(int)
    Wheel = QtCore.Signal(int)
    mousePressLeft = QtCore.Signal()
    mousePressRight = QtCore.Signal()
    mouseReleaseLeft = QtCore.Signal()
    mouseReleaseRight = QtCore.Signal()
    # mouseLeft = QtCore.Signal(int)
    # mouseLeft = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(GlobalMouse, self).__init__( parent)
        # create a hook manager
        hm = pyHook.HookManager()
        # watch for all key down events
        hm.MouseAll = self.OnMouseEvent
        # set the hook
        hm.HookMouse()
        self._wheel = 0

    def OnMouseEvent(self, event):
        """# called when mouse events are received
        print('MessageName:',event.MessageName)
        print('Message:',event.Message)
        print('Time:',event.Time)
        print('Window:',event.Window)
        print('WindowName:',event.WindowName)
        print('Position:',event.Position)
        print('Wheel:',event.Wheel)
        print('Injected:',event.Injected)
        print('---'"""
        position = event.Position
        self.Position[object].emit(position)
        self.Position[int, int].emit(*position)
        self.PositionX.emit(position[0])
        self.PositionY.emit(position[1])
        self.WheelSens.emit(event.Wheel)
        self._wheel += event.Wheel
        self.Wheel.emit(self._wheel)
        message = event.Message
        if message == 513:
            self.mousePressLeft.emit()
        elif message == 514:
            self.mouseReleaseLeft.emit()
        elif message == 516:
            self.mousePressRight.emit()
        elif message == 517:
            self.mouseReleaseRight.emit()
        return True  # return True to pass the event to other handlers


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = GlobalMouse()
    sys.exit(app.exec_())