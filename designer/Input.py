# -*- coding: utf-8 -*-
from PySide6 import QtCore, QtGui, QtWidgets
from SmartFramework.tools.objects import add_Args


class Input(QtCore.QObject):
    """cet objet sert à rajouter une entrée à un patch qui sera ajouté sousforme de slot à la compilation"""

    output = QtCore.Signal((object,), (bool,), (int,), (float,), (str,))

    def __init__(self, parent=None, value="", signal=True, argument=True):
        # oblige de mettre '_' a la fin de property sinon uic n'arrive pas a compiler
        super(Input, self).__init__(parent)
        add_Args(locals())
