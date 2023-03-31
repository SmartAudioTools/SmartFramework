from qtpy import QtCore, QtGui, QtWidgets
import pyHook


class GlobalKey(QtCore.QObject):

    Key = QtCore.Signal(str)  # objet en premier pour etre par defaut
    KeyID = QtCore.Signal(int)
    Ascii = QtCore.Signal((str,), (int,))

    def __init__(self, parent=None):
        super(GlobalKey, self).__init__(parent)
        # create a hook manager
        hm = pyHook.HookManager()
        # watch for all key down events
        hm.KeyDown = self.OnKeyboardEvent
        # set the hook
        hm.HookKeyboard()

    def OnKeyboardEvent(self, event):
        """
        print('MessageName:',event.MessageName)
        print('Message:',event.Message)
        print('Time:',event.Time)
        print('Window:',event.Window)
        print('WindowName:',event.WindowName)
        print('Ascii:', event.Ascii, chr(event.Ascii))
        print('Key:', event.Key)
        print('KeyID:', event.KeyID)
        print('ScanCode:', event.ScanCode)
        print('Extended:', event.Extended)
        print('Injected:', event.Injected)
        print('Alt', event.Alt)
        print('Transition', event.Transition)
        print('---')
        """
        self.Key.emit(event.Key)
        self.KeyID.emit(event.KeyID)
        self.Ascii[int].emit(event.Ascii)
        self.Ascii[str].emit(chr(event.Ascii))
        return True  # return True to pass the event to other handlers


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = GlobalKey()
    sys.exit(app.exec_())