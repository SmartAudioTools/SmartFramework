# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 21:18:26 2021

@author: Baptiste
"""
import sys
import qtpy.QtWidgets

app = qtpy.QtWidgets.QApplication(sys.argv)
from SmartFramework.serialize.tools import instance
import PyQt5.sip
import qtpy.QtCore
import qtpy.QtGui
import qtpy.QtWidgets

obj = qtpy.QtWidgets.QPushButton(parent=None)
obj.setAcceptDrops(False)
obj.setAccessibleDescription("")
obj.setAccessibleName("")
obj.setAutoDefault(False)
obj.setAutoExclusive(False)
obj.setAutoFillBackground(False)
obj.setAutoRepeat(False)
obj.setAutoRepeatDelay(300)
obj.setAutoRepeatInterval(100)
obj.setBackgroundRole(PyQt5.sip._unpickle_enum("PyQt5.QtGui", "ColorRole", 1))
obj.setBaseSize(qtpy.QtCore.QSize(0, 0))
obj.setCheckable(False)
obj.setChecked(False)
obj.setContentsMargins(qtpy.QtCore.QMargins(0, 0, 0, 0))
obj.setContextMenuPolicy(
    PyQt5.sip._unpickle_enum("PyQt5.QtCore", "ContextMenuPolicy", 1)
)
obj.setCursor(
    instance(
        qtpy.QtGui.QCursor(),
        pos=qtpy.QtCore.QPoint(850, 339),
        shape=PyQt5.sip._unpickle_enum("PyQt5.QtCore", "CursorShape", 0),
    )
)
obj.setDefault(False)
obj.setDown(False)
obj.setEnabled(True)
obj.setFlat(False)
obj.setFocusPolicy(PyQt5.sip._unpickle_enum("PyQt5.QtCore", "FocusPolicy", 11))
obj.setFocusProxy(None)
obj.setFont(
    instance(
        qtpy.QtGui.QFont(),
        bold=False,
        capitalization=PyQt5.sip._unpickle_enum("PyQt5.QtGui", "Capitalization", 0),
        family="MS Shell Dlg 2",
        fixedPitch=False,
        hintingPreference=PyQt5.sip._unpickle_enum(
            "PyQt5.QtGui", "HintingPreference", 0
        ),
        italic=False,
        kerning=True,
        letterSpacing=0.0,
        letterSpacingType=PyQt5.sip._unpickle_enum("PyQt5.QtGui", "SpacingType", 0),
        overline=False,
        pixelSize=-1,
        pointSize=8,
        pointSizeF=7.875,
        rawMode=False,
        rawName="unknown",
        stretch=0,
        strikeOut=False,
        style=PyQt5.sip._unpickle_enum("PyQt5.QtGui", "Style", 0),
        styleHint=PyQt5.sip._unpickle_enum("PyQt5.QtGui", "StyleHint", 5),
        styleName="",
        styleStrategy=PyQt5.sip._unpickle_enum("PyQt5.QtGui", "StyleStrategy", 1),
        underline=False,
        weight=50,
        wordSpacing=0.0,
    )
)
obj.setForegroundRole(PyQt5.sip._unpickle_enum("PyQt5.QtGui", "ColorRole", 8))
obj.setGeometry(qtpy.QtCore.QRect(0, 0, 640, 480))
obj.setGraphicsEffect(None)
obj.setHidden(True)
obj.setIcon(
    instance(
        qtpy.QtGui.QIcon(),
        fallbackSearchPaths=[],
        isMask=False,
        themeName="",
        themeSearchPaths=[":/icons"],
    )
)
obj.setIconSize(qtpy.QtCore.QSize(32, 32))
obj.setInputMethodHints(qtpy.QtCore.Qt.InputMethodHints(0))
obj.setLayout(None)
obj.setLayoutDirection(PyQt5.sip._unpickle_enum("PyQt5.QtCore", "LayoutDirection", 0))
obj.setLocale(instance(qtpy.QtCore.QLocale(), numberOptions=already_serialized))
obj.setMask(instance(qtpy.QtGui.QRegion(), rects=[]))
obj.setMaximumHeight(16777215)
obj.setMaximumSize(qtpy.QtCore.QSize(16777215, 16777215))
obj.setMaximumWidth(16777215)
obj.setMenu(None)
obj.setMinimumHeight(0)
obj.setMinimumSize(qtpy.QtCore.QSize(0, 0))
obj.setMinimumWidth(0)
obj.setObjectName("")
obj.setPalette(instance(qtpy.QtGui.QPalette(), currentColorGroup=already_serialized))
obj.setShortcut(qtpy.QtGui.QKeySequence(0, 0, 0, 0))
obj.setSizeIncrement(qtpy.QtCore.QSize(0, 0))
obj.setSizePolicy(
    instance(
        qtpy.QtWidgets.QSizePolicy(),
        controlType=PyQt5.sip._unpickle_enum("PyQt5.QtWidgets", "ControlType", 512),
        horizontalPolicy=PyQt5.sip._unpickle_enum("PyQt5.QtWidgets", "Policy", 1),
        horizontalStretch=0,
        retainSizeWhenHidden=False,
        verticalPolicy=PyQt5.sip._unpickle_enum("PyQt5.QtWidgets", "Policy", 0),
        verticalStretch=0,
    )
)
obj.setStatusTip("")
obj.setStyle(instance(qtpy.QtWidgets.QCommonStyle(), objectName="windowsvista"))
obj.setStyleSheet("")
obj.setText("")
obj.setToolTip("")
obj.setToolTipDuration(-1)
obj.setUpdatesEnabled(True)
obj.setVisible(False)
obj.setWhatsThis("")
obj.setWindowFilePath("")
obj.setWindowIcon(
    instance(
        qtpy.QtGui.QIcon(),
        fallbackSearchPaths=[],
        isMask=False,
        themeName="",
        themeSearchPaths=[":/icons"],
    )
)
obj.setWindowIconText("")
obj.setWindowModality(PyQt5.sip._unpickle_enum("PyQt5.QtCore", "WindowModality", 0))
obj.setWindowModified(False)
obj.setWindowOpacity(1.0)
obj.setWindowRole("")
obj.setWindowState(qtpy.QtCore.Qt.WindowStates())
obj.setWindowTitle("")
