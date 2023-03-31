from qtpy import QtCore, QtGui, QtWidgets, scaled
from SmartFramework.tools.dictionaries import reverseDict
import math
from SmartFramework.serialize.serializejson import dumps, loads
from SmartFramework.sync.Sync import Sync
from qtpy.QtWidgets import *
import os

os.environ["QT_API"] = "PyQt6"
os.environ["FORCE_QT_API"] = " "

eventNames = reverseDict(QtCore.QEvent.__dict__)
trackpadHack = True  # True
debug = False  # True
DEFAULT = 0
X_ABSOLUTE = 1
X_RELATIVE = 2
Y_ABSOLUTE = 3
Y_RELATIVE = 4
Y_DYNAMIC_SCALE_TO_SCREEN = 5
VALUES = 6
CONTROLS = 7
INCONTROLS = 8

UP = 0
DOWN = 1
# ONSELECTED = 3


def getDecimals(f):
    d = 0
    while f - round(f, d):
        d += 1
    return d


if debug:
    from SmartFramework.tools.dictionaries import reverseDict

    eventNames = reverseDict(QtCore.QEvent.__dict__)


class DebugdApp(QtWidgets.QApplication):
    def __init__(self, *args):
        QtWidgets.QApplication.__init__(self, *args)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        eventType = event.type()
        if eventType == QtCore.QEvent.TouchBegin:
            print("TouchBegin", obj)
        if eventType == QtCore.QEvent.TouchUpdate:
            print("TouchUpdate", obj)
        return False


class Struct:
    def __init__(self, argDict):
        d = {}
        for key, value in argDict.items():
            if isinstance(value, dict):
                value = Struct(value)
            d[key] = value
        self.__dict__ = d

    def __getitem__(self, attributeStr):
        return self.__dict__[attributeStr]


def QColor(color):
    if isinstance(color, QtGui.QColor) or color is None:
        return color
    return QtGui.QColor(*color)


class ControlUI(QtWidgets.QComboBox):
    """
    ControlUI est un widget heritant de QComboBox hautement paramétrable qui peut remplacer :
    QPushButton
    QCheckBox
    QRadioButton ?
    QSpinBox
    QDoubleSpinBox
    QSlider

    Il peut etre controler avec une souris, touch pad, touch screen.
    Lors d'une utilisation comme un QComboBox, les items peuvent être initialisé avec une liste (comme QCombox) mais aussi avec un dictionnaire, permetant alors de donner des noms à des valeurs , les noms seront affichés et les valeure envoyées.
    """

    valueChanged = QtCore.Signal((int,), (float,), (str,), (bool,), (object,))
    # valueEditing = QtCore.Signal(bool)  # idem que clicked (intervient just plus tôt?)
    # QPushButton : This signal is emitted when the button is activated (i.e., pressed down then released while the mouse cursor is inside the button), when the shortcut key is typed, or when click() or animateClick() is called. Notably, this signal is not emitted if you call setDown(), setChecked() or toggle(). If the button is checkable, checked is true if the button is checked, or false if the button is unchecked.:
    clicked = QtCore.Signal(bool)
    pressed = QtCore.Signal()  # choix de ce nom pour compatibilité avec QPushButton
    released = QtCore.Signal()  # choix de ce nom pour compatibilité avec QPushButton
    toggled = QtCore.Signal(bool)  # =valuChanged[bool] for QPushButtton compatibility
    outControlName = QtCore.Signal(str)
    outInControlName = QtCore.Signal(str)

    def __init__(
        self,
        parent=None,
        value=0,
        minimum=0,
        maximum=127,
        decimals=0,
        singleStep=0,
        pageStep=0,
        displayMinimum=None,
        displayMaximum=None,
        curve="",
        prefix="",
        suffix="",
        text="",
        repeat=False,
        items={},
        # permet editer le dictionnaire dans une propriété str dans QtDesigner ?:
        itemsDictStr="",
        checkable=False,
        checked=False,
        readOnly=False,
        tracking=True,
        sendInitValue=True,
        sendSetValue=True,
        mouseSensibility=0.1,
        # controls
        inControlNames=None,
        inControlName=None,
        controlNames=None,
        controlName=None,
        # sync & serialization
        # serialize=True,
        syncModule="synced",
        syncName="",
        syncSave=True,
        # style
        indent=5,  # indentation in pixelss
        alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
        penWidth=1.0,
        fill=False,
        fillColor=(0, 0, 0, 10),
        borderDraw=True,
        borderBack=True,
        borderColor=(0, 0, 0, 30),
        barBorderColor=(100, 210, 0, 255),
        barFillColor=(100, 210, 0, 100),
        cornerRadius=6,
        isTime=False,
        **kwargs,
    ):
        self._istime = isTime
        self._visiblePopup = False
        QtWidgets.QComboBox.__init__(self, parent, **kwargs)
        # synchronisation & serialization
        self._readOnly = readOnly
        self.setStyleSheet("QListView{outline: 0;}")
        self._tracking = tracking

        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.MinimumExpanding,
                QtWidgets.QSizePolicy.MinimumExpanding,
            )
        )
        self._valueEditing = False
        self._checked = None
        self._penWidth = penWidth
        self._fill = fill
        self._fillColor = QColor(fillColor)
        self._borderDraw = borderDraw
        self._borderBack = borderBack
        self._borderColor = QColor(borderColor)
        self._barBorderColor = QColor(barBorderColor)
        self._barFillColor = QColor(barFillColor)

        self._cornerRadius = cornerRadius
        self._listView = self.view()
        self.installEventFilter(self)
        self._listView.installEventFilter(self)
        self._listView.window().installEventFilter(self)
        self._listView.viewport().installEventFilter(self)
        self.setAttribute(
            QtCore.Qt.WA_AcceptTouchEvents, True
        )  # permet de detecter un touch event
        # je n'arrive pas à attraper toucheEvent en l'activant dans un wiget quand un menu type "whammy" est affiché
        # en utilisant debugApp, je vois qu'une windows recoit les touchUpdate mais elle n'a ni parent() ni children()
        # self._listView.setAttribute(QtCore.Qt.WA_AcceptTouchEvents,True)
        # self._listView.window().setAttribute(QtCore.Qt.WA_AcceptTouchEvents,True) # permet de detecter un touch event
        # self._listView.viewport().setAttribute(QtCore.Qt.WA_AcceptTouchEvents,True) # permet de detecter un touch event
        # for child in  self.children():
        #    if type(child) is QtWidgets.QFrame :
        #        child.setAttribute(QtCore.Qt.WA_AcceptTouchEvents,True)
        self._spaceWidth = QtGui.QFontMetrics(self.font()).width(" ")
        self._touchMode = None
        self._mouseMode = None
        self._sync = Sync(self, syncModule=syncModule, syncName=syncName, save=syncSave)
        self.valueChanged[object].connect(self._sync.input)
        self._sync.output[object].connect(self.setValue)
        # pour compatibiité avec QPushButton
        self.valueChanged[bool].connect(self.toggled)
        # self._serialize = serialize
        self._lastPopup = None
        self._controlNames = []
        self._controlName = ""
        self._controlShortName = ""
        self._inControlNames = []
        self._inControlName = ""
        self.setText(text)
        self.setPrefix(prefix)
        self.setSuffix(suffix)
        self.setCheckable(checkable)
        self.setInControlNames(inControlNames)
        if inControlName is not None:
            self.setInControlName(inControlName)
        self.setControlNames(controlNames)
        if controlName is not None:
            self.setControlName(controlName)

        # self.setButtonSymbols(buttonSymbols)

        # limites et mapping
        self._value = None  # None fait planter qtdesigner
        self._decimals = decimals
        self._singleStep = singleStep
        self._pageStep = pageStep
        self._minimum = minimum
        self._maximum = maximum
        self._displayMaximum = displayMaximum
        self._displayMinimum = displayMinimum
        # self.setDisplayMinimum(displayMinimum)
        # self.setDisplayMaximum(displayMaximum)
        self._curve = curve

        if itemsDictStr:
            self.setItemsDictStr(itemsDictStr)
        else:
            self.setItems(items)  # doit etre mis après self._maximum = maximum
        # properties
        self.mouseSensibility = mouseSensibility
        self._repeat = repeat
        self.setAlignment(
            alignment
        )  # & QtCore.Qt.AlignVCenter  #QtCore.Qt.AlignCenter #QtCore.Qt.AlignRight#QtCore.Qt.AlignLeft#| QtCore.Qt.AlignBottom #QtCore.Qt.AlignVCenter

        # intern
        self._sendInitValue = sendInitValue
        self._sendSetValue = sendSetValue
        self._initValue = value
        self._initialized = False
        self.setIndent(indent)
        self._mode = Struct(
            {
                "mouse": {
                    "pressLeft": {
                        "press": DEFAULT,
                        "moveX": X_ABSOLUTE,
                        "moveY": None,
                        "moveXYsepThreshold": 3,
                        "dragUp": None  # {
                        # "threshold": 50,
                        # "leftZone":  CONTROLS,
                        # "rightZone": INCONTROLS
                        # }
                    },
                    "pressRight": {
                        "press": {"leftZone": CONTROLS, "rightZone": INCONTROLS}
                    },
                },
                "touch": {
                    "pressFirst": {
                        "press": DEFAULT,
                        "moveX": X_ABSOLUTE,
                        "moveY": None,
                        "moveXYsepThreshold": 3,
                        "dragUp": {
                            "threshold": 50,
                            "leftZone": CONTROLS,
                            "rightZone": INCONTROLS,
                        },
                    }
                },
            }
        )
        self._methode_from_key = {
            QtCore.Qt.Key_Up: self.stepUp,
            QtCore.Qt.Key_Right: self.stepRight,
            QtCore.Qt.Key_Down: self.stepDown,
            QtCore.Qt.Key_Left: self.stepLeft,
            # QtCore.Qt.Key_Space: self.incrementValue,
        }
        # self._desktopWidget = QtWidgets.QDesktopWidget()
        self._visiblePopup = False
        # self.setMinimumSize(10, QtGui.QFontMetrics(self.font()).height())

        if trackpadHack:
            # Hack pour corriger pb de clic-droit + drag sur macbook pro
            self._trackpadLeftPressTimer = QtCore.QTimer()
            self._trackpadLeftPressTimer.setInterval(1)
            self._trackpadLeftPressTimer.timeout.connect(self.trackpadSheduledLeftPress)
            self._trackpadLeftPressTimer.setSingleShot(True)
            self._trackpadLeftReleaseTimer = QtCore.QTimer()
            self._trackpadLeftReleaseTimer.setInterval(1)
            self._trackpadLeftReleaseTimer.timeout.connect(
                self.trackpadSheduledRightRelease
            )
            self._trackpadLeftReleaseTimer.setSingleShot(True)
            self._trackpadPressingRight = False
            self._trackpadPressingLeft = False

        self.updateTrueDecimalsAndSingleStep()
        self.updateMaxDigit()
        self.setChecked(checked)
        self.currentIndexChanged[int].connect(self.updatePopUpSelectedItem)
        QtCore.QTimer.singleShot(
            0, self.setInitValue
        )  # permet d'attendre que les connexion ai été crées.

    # def sizeHint(self):
    #    # return QtCore.QSize(self.getMaxPrintedWidth(), 35)  #        self.setSizePolicy(#
    #
    #    #self.setMinimumSize(self._maximum - self._minimum, 35)
    #
    #    return QtCore.QSize(self._maximum - self._minimum, 35)  #

    def normalizePoint(self, screenPos):
        # QGuiApplication::screens
        screenGeometry = self._desktopWidget.screenGeometry(screenPos)
        return QtCore.QPointF(
            screenPos.x() / screenGeometry.width(),
            screenPos.y() / screenGeometry.height(),
        )

    # SpinBox properties -> slots
    def cleanItems(self):
        self._lastPopup = None
        self._itemsDict = {}
        self._itemsIndexFromValue = {}
        self._items = []
        self._itemsIndexFromValue
        self._maxPrintedWidth = None
        # self.clear() # fou la merde, car en faisant clear, il met le itemIndex à -1, ce qui emet un signal currentIndexChanged , et efface self._controlName dans

    @QtCore.Slot(object)
    def setParameters(self, parameters):
        parameters_is_none = parameters is None
        if parameters_is_none:
            parameters = {}
        self.cleanItems()
        self.setText(parameters.get("text", ""))
        self.setPrefix(parameters.get("prefix", ""))
        self.setSuffix(parameters.get("suffix", ""))
        self.setCheckable(parameters.get("checkable", False))

        # limites et mapping
        self._value = None
        self._decimals = parameters.get("decimals", 0)
        self._minimum = parameters.get("minimum", parameters.get("min", 0))
        self._maximum = parameters.get("maximum", parameters.get("max", 127))
        self.updateTrueDecimalsAndSingleStep()
        self.setDisplayMinimum(
            parameters.get("displayMinimum", parameters.get("displayMin", None))
        )
        self.setDisplayMaximum(
            parameters.get("displayMaximum", parameters.get("displayMax", None))
        )
        self._curve = parameters.get("curve", "")
        self.setItems(
            parameters.get("items", {})
        )  # doit etre mis après self._maximum = maximum
        # if len(parameters):
        if parameters_is_none:
            self._value = None
            self.update()
        else:
            self._setNumberValue(parameters.get("value", 0))

    def updateParameters(self, parameters):
        pass

    @QtCore.Slot(bool)
    def setTracking(self, tracking):
        self._tracking = tracking

    def getTracking(self):
        return self._tracking

    tracking = QtCore.Property(
        bool, getTracking, setTracking
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)

    @QtCore.Slot(bool)
    def setReadOnly(self, readOnly):
        self._readOnly = readOnly

    def isReadOnly(self):
        return self._readOnly

    readOnly = QtCore.Property(
        bool, isReadOnly, setReadOnly
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)

    @QtCore.Slot(str)
    def setText(self, text):
        self.cleanItems()
        self._text = text
        self._contentText = text

    def getText(self):
        return self._text

    text = QtCore.Property(
        str, getText, setText
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)

    def getEnableDrag(self):
        return (not self._text) and (not self._items)  # or (len(self._items) > 3)

    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setMinimum(self, value):
        self._minimum = value
        self._maxPrintedWidth = None
        self.updateTrueDecimalsAndSingleStep()
        self.updateMaxDigit()

    def updateMinimumSize(self):
        # self._maximum - self._minimum
        self.setMinimumSize(self.getMaxPrintedWidth(), 35)

    def getMinimum(self):
        return self._minimum

    minimum = QtCore.Property(
        float, getMinimum, setMinimum
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)

    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setMaximum(self, value):
        self._maximum = value
        self._maxPrintedWidth = None
        self.updateTrueDecimalsAndSingleStep()
        self.updateMaxDigit()

    def getMaximum(self):
        return self._maximum

    maximum = QtCore.Property(
        float, getMaximum, setMaximum
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme (car pas defini de get?)

    def setRange(self, minimum, maximum):
        self._minimum = minimum
        self._maximum = maximum
        self._maxPrintedWidth = None
        self.updateTrueDecimalsAndSingleStep()

    @QtCore.Slot(object)  # pour pouvoir prendre none
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setDisplayMinimum(self, value):
        self._displayMinimum = value
        self._maxPrintedWidth = None
        self.updateMaxDigit()

    def getDisplayMinimum(self):
        if self._displayMinimum is not None:
            return self._displayMinimum
        else:
            return self._minimum

    displayMinimum = QtCore.Property(
        float, getDisplayMinimum, setDisplayMinimum
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)

    @QtCore.Slot(object)  # pour pouvoir prendre none
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setDisplayMaximum(self, value):
        self._displayMaximum = value
        self._maxPrintedWidth = None
        self.updateMaxDigit()

    def getDisplayMaximum(self):
        if self._displayMaximum is not None:
            return self._displayMaximum
        else:
            return self._maximum

    displayMaximum = QtCore.Property(
        float, getDisplayMaximum, setDisplayMaximum
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme (car pas defini de get?)

    # properties

    def setRepeat(self, value):
        self._repeat = value

    def getRepeat(self):
        return self._repeat

    repeat = QtCore.Property(bool, getRepeat, setRepeat)

    @QtCore.Slot(str)
    def setPrefix(self, string):
        self._prefix = string
        self._maxPrintedWidth = None
        self.update()

    def getPrefix(self):
        return self._prefix

    prefix = QtCore.Property(str, getPrefix, setPrefix)

    @QtCore.Slot(str)
    def setSuffix(self, string):
        self._suffix = string
        if string:
            self._suffixWithSpace = string
        else:
            self._suffixWithSpace = ""
        self._maxPrintedWidth = None
        self.update()

    def getSuffix(self):
        return self._suffix

    suffix = QtCore.Property(str, getSuffix, setSuffix)

    @QtCore.Slot(int)
    def setDecimals(self, value):
        self._decimals = value
        self._maxPrintedWidth = None
        self.updateTrueDecimalsAndSingleStep()

    def getDecimals(self):
        return self._trueDecimals

    decimals = QtCore.Property(int, getDecimals, setDecimals)

    def updateTrueDecimalsAndSingleStep(self):
        if self._singleStep:
            self._trueDecimals = max(
                (
                    self._decimals,
                    getDecimals(self._minimum),
                    getDecimals(self._maximum),
                    getDecimals(self._singleStep),
                )
            )
            self._trueSingleStep = self._singleStep
        else:
            self._trueDecimals = max(
                (self._decimals, getDecimals(self._minimum), getDecimals(self._maximum))
            )
            self._trueSingleStep = 10 ** (-self._trueDecimals)
        if self._trueDecimals:
            self._minimum = float(
                self._minimum
            )  # permet d'afficher 0.0 et pas 0 quand veut utiliser le ControlUI comme un QDoubleSpinbox
            self._maximum = float(
                self._maximum
            )  # permet d'afficher 128.0 et pas 128 quand veut utiliser le ControlUI comme un QDoubleSpinbox
        self.updateMinimumSize()

    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setSingleStep(self, value):
        self._singleStep = value
        self.updateTrueDecimalsAndSingleStep()

    def getSingleStep(self):
        return self._trueSingleStep

    singleStep = QtCore.Property(float, getSingleStep, setSingleStep)

    @QtCore.Slot(float)
    @QtCore.Slot(int)
    def setPageStep(self, value):
        self._pageStep = value
        # self.updateTrueDecimalsAndSingleStep()

    def getPageStep(self):
        return self._pageStep

    pageStep = QtCore.Property(float, getPageStep, setPageStep)

    @QtCore.Slot(str)
    def setCurve(self, curve):
        self._curve = curve

    def getCurve(self):
        return self._curve

    curve = QtCore.Property(str, getCurve, setCurve)

    @QtCore.Slot(object)
    def setItems(self, items):
        if items is None:
            items = []  # {} # evit de planter quand teste len(self._items)
        if isinstance(items, dict):
            self._itemsDict = items
            self._itemsIndexFromValue = {
                value: index for index, value in enumerate(items.values())
            }
            # self._itemValues = list(items.values())
            items = list(items.keys())
        else:
            self._itemsDict = {}
            self._itemsIndexFromValue = {}
        # self._lastPopup = VALUES
        # self.clear()
        self._maxPrintedWidth = None
        self._items = items
        if items:
            self._minimum = 0
            self._maximum = len(items) - 1
            # QtWidgets.QComboBox.addItems(self,items)
            self.setMaxVisibleItems(len(items))

    def getItems(self):
        return self._items

    items = QtCore.Property(list, getItems, setItems)

    def getItemsDictStr(self):
        if self._itemsDict:
            return dumps(self._itemsDict, indent=None, sort_keys=False)
        else:
            return ""

    def setItemsDictStr(self, itemsDictStr):
        if itemsDictStr:
            self.setItems(loads(itemsDictStr))
        else:
            self.setItem(None)

    itemsDictStr = QtCore.Property(str, getItemsDictStr, setItemsDictStr)

    def setPopItems(self, items):
        self.blockSignals(True)
        self.clear()
        if items:
            QtWidgets.QComboBox.addItems(self, items)
            self.setMaxVisibleItems(len(items))
            # self.setCurrentIndex(-1) # mauvaise idée permet de detecter meme si on reprend
            fm = QtGui.QFontMetrics(self.font())
            screenSize = self.window().windowHandle().screen().size()  # .height()
            frameContentSize = fm.size(
                0, "\n".join(items)
            )  # je n'ai pas trouvé comment faire autrement
            self._frameSize = QtCore.QSize(
                min(screenSize.width(), frameContentSize.width() + 8),
                min(screenSize.height(), frameContentSize.height() + 2),
            )
        self.blockSignals(False)

    def setSendInitValue(self, value):
        self._sendInitValue = value

    def getSendInitValue(self):
        return self._sendInitValue

    sendInitValue = QtCore.Property(bool, getSendInitValue, setSendInitValue)

    def setSendSetValue(self, value):
        self._sendSetValue = value

    def getSendSetValue(self):
        return self._sendSetValue

    sendSetValue = QtCore.Property(bool, getSendSetValue, setSendSetValue)

    def setMouseSensibility(self, value):
        self._mouseSensibility = value

    def getMouseSensibility(self):
        return self._mouseSensibility

    mouseSensibility = QtCore.Property(float, getMouseSensibility, setMouseSensibility)

    # intern
    def setInitValue(self):
        if (
            not self._initialized
        ):  # il faut avant s'assurer que n'a pas été intialisé par deserialisation
            self._setNumberValue(self._initValue, fromSetInitValue=True)
        self._initialized = True

    def tabletEvent(self, event):
        if (
            event.type() == QtCore.QEvent.TabletMove
            and event.pressure() > 0.0
            and self.getEnableDrag()
        ):
            newY = event.globalPosF().y()
            if self._oldY is not None:
                deltaY = newY - self._oldY
                self.incrementFloatValue(
                    -deltaY * self._mouseSensibility * self.singleStep
                )
            self._oldY = newY
            # self._draging = True
        elif event.type() == QtCore.QEvent.TabletPress:
            self._oldY = event.globalPosF().y()
            self._floatValue = self.value
            if not self.getEnableDrag() and self._items:
                self.incrementValue(1)
        elif event.type() == QtCore.QEvent.TabletRelease:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def incrementFloatValue(self, inc):
        """ "incrementation circulaire si self._items"""
        self._floatValue += inc
        if self._items:
            if self._floatValue < self.minimum:
                self._floatValue = self._maximum
            elif self._floatValue > self._maximum:
                self._floatValue = self._minimum
        self._setNumberValue(self._floatValue)

    def incrementValue(self, inc):
        """ "incrementation circulaire si self._items"""
        value = self._value + inc
        if self._items:
            if value < self.minimum:
                value = self._maximum
            elif value > self._maximum:
                value = self._minimum
        self._setNumberValue(value)

    def event(self, event, toucheUpdateFromMouse=False):
        eventType = event.type()
        if eventType == QtCore.QEvent.TouchBegin:
            self._mouseLastPos = self._mouseBeginPos = QtGui.QCursor.pos()
            if debug:
                print("TouchBegin")
            self._disableDragUpDown = False
            self._touchMode = self._mode.touch.pressFirst.press
            if not self.showPopupType(self._touchMode, DOWN):
                self.press(globalPosition=event.touchPoints()[0].screenPos())
            event.accept()  # utile ?
            return True
        if eventType == QtCore.QEvent.TouchEnd:
            if debug:
                print("TouchEnd")
            self._touchMode = None
            self.release()
            if self._visiblePopup:
                QtCore.QTimer.singleShot(1, self.hidePopup)
            event.accept()  # utile ?
            return True
        if eventType == QtCore.QEvent.TouchUpdate or toucheUpdateFromMouse:
            if debug:
                print(".", end="")
            if toucheUpdateFromMouse:
                pos = event.screenPos()
                lastPos = self._mouseLastPos
                deltaPos = pos - self._mouseBeginPos
            else:
                touchPoint = event.touchPoints()[0]
                pos = touchPoint.screenPos()
                lastPos = touchPoint.lastScreenPos()
                deltaPos = pos - touchPoint.startScreenPos()
            if pos != lastPos:
                pressFirst = self._mode.touch.pressFirst
                if abs(deltaPos.x()) > 30 and self.getEnableDrag():
                    self._disableDragUpDown = True
                elif not self._disableDragUpDown:
                    midleUpPoint = self.mapToGlobal(
                        QtCore.QPoint(int(self.width() * 0.5), 0)
                    )
                    if pressFirst.dragUp and pos.y() < midleUpPoint.y():
                        if pos.x() < midleUpPoint.x():  # leftZone
                            self._touchMode = pressFirst.dragUp.leftZone
                        else:
                            self._touchMode = pressFirst.dragUp.rightZone
                        self._disableDragUpDown = True
                        self.showPopupType(self._touchMode, UP)
                    elif self._items and self._checkable and deltaPos.y() > 10:
                        self.showPopupType(VALUES, DOWN)
                if not self._touchMode:  # DEFAULT ou None
                    moveXYsepThreshold = pressFirst.moveXYsepThreshold
                    moveX = pressFirst.moveX
                    moveY = pressFirst.moveY
                    if moveX is None:
                        self._touchMode = moveY  # Y_DYNAMIC_SCALE_TO_SCREEN
                    elif moveY is None:
                        self._touchMode = moveX
                    elif (
                        abs(deltaPos.x()) >= moveXYsepThreshold
                        or abs(deltaPos.y()) >= moveXYsepThreshold
                    ):
                        if abs(deltaPos.x()) < abs(deltaPos.y()):
                            self._touchMode = moveY  # Y_DYNAMIC_SCALE_TO_SCREEN
                        else:
                            self._touchMode = moveX  # X_ABSOLUTE
                self.move(pos, lastPos, self._touchMode, repositionable=False)
            event.accept()
            self._mouseLastPos = QtGui.QCursor.pos()
            return True

        if (
            debug
            and (eventType in eventNames)
            and (eventType not in [QtCore.QEvent.HoverMove])
        ):
            print(eventNames[eventType])
        """if eventType in [QtCore.QEvent.FocusOut,QtCore.QEvent.FocusIn,QtCore.QEvent.ActivationChange,QtCore.QEvent.Leave,QtCore.QEvent.HoverLeave,QtCore.QEvent.Enter,QtCore.QEvent.HoverEnter   ]:
            print("tente blocage repaint intempestifs")
            return True"""
        return QtWidgets.QComboBox.event(self, event)

    # def reactiveMouse(self):
    #    self._useTouchScreen = False

    def mouseMoveEvent(self, event):
        if self._readOnly:
            return
        if self._mouseLastPos:
            if debug:
                print("mouseMouveEvent")
            if event.buttons() == QtCore.Qt.LeftButton:
                # if self.getEnableDrag() :
                pos = (
                    QtGui.QCursor.pos()
                )  # event.globalPos() pas la meme chose ! global position est relatif à la fenetre principale par l'ecran !
                lastPos = self._mouseLastPos
                if pos != lastPos:
                    pressLeft = self._mode.mouse.pressLeft
                    deltaPos = pos - self._mouseBeginPos
                    if abs(deltaPos.x()) > 30 and self.getEnableDrag():
                        self._disableDragUpDown = True
                    elif not self._disableDragUpDown:
                        midleUpPoint = self.mapToGlobal(
                            QtCore.QPoint(int(self.width() * 0.5), 0)
                        )
                        if pressLeft.dragUp and pos.y() < midleUpPoint.y():
                            if pos.x() < midleUpPoint.x():  # leftZone
                                self._mouseMode = pressLeft.dragUp.leftZone
                            else:
                                self._mouseMode = pressLeft.dragUp.rightZone
                            self.hidePopup()
                            self.showPopupType(self._mouseMode, UP)
                        elif self._items and self._checkable and deltaPos.y() > 10:
                            self.showPopupType(VALUES, DOWN)
                    if not self._mouseMode:  # DEFAULT ou None
                        moveXYsepThreshold = pressLeft.moveXYsepThreshold
                        moveX = pressLeft.moveX
                        moveY = pressLeft.moveY
                        if moveX is None:
                            self._mouseMode = moveY  # Y_DYNAMIC_SCALE_TO_SCREEN
                        elif moveY is None:
                            self._mouseMode = moveX
                        elif (
                            abs(deltaPos.x()) >= moveXYsepThreshold
                            or abs(deltaPos.y()) >= moveXYsepThreshold
                        ):
                            if abs(deltaPos.x()) < abs(deltaPos.y()):
                                self._mouseMode = moveY  # Y_DYNAMIC_SCALE_TO_SCREEN
                            else:
                                self._mouseMode = moveX  # X_ABSOLUTE
                    self.move(pos, lastPos, self._mouseMode)
                    self._mouseLastPos = QtGui.QCursor.pos()

            #    if mode == INCONTROLS:
            # if self._inControlNames and not self._visiblePopup:   # self.view().isVisible() reste false tant que pas fini de deplier !?
            #    self.showPopupType(mode)

    def move(self, screenPos, lastScreenPos, mode, repositionable=True):
        if self.getEnableDrag():
            if mode == X_ABSOLUTE:
                # print(self.mapFromGlobal(screenPos).x())
                self._setNumberValue(
                    self.mapFromGlobalF(screenPos).x()
                    * (self._maximum - self._minimum)
                    / self.size().width()
                    + self._minimum
                )
            elif mode == Y_RELATIVE:
                self.incrementFloatValue(
                    -(screenPos - lastScreenPos).y()
                    * self._mouseSensibility
                    * 10 ** (-self._trueDecimals)
                )
                if repositionable:
                    self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
                    QtGui.QCursor.setPos(
                        lastScreenPos
                    )  # ne marche pas sur pipo quand utilise le doigt....
            elif mode == Y_DYNAMIC_SCALE_TO_SCREEN:
                normalizedPos = self.normalizePoint(screenPos)
                lastNormalizedPos = self.normalizePoint(lastScreenPos)
                lastNormalizedY = lastNormalizedPos.y()
                deltaNormalizedY = normalizedPos.y() - lastNormalizedY
                if deltaNormalizedY != 0.0:
                    marge = 0.02
                    if deltaNormalizedY < 0:
                        if normalizedPos.y() < marge:
                            self._floatValue = self._maximum
                        else:
                            self._floatValue -= (
                                (self._maximum - self._floatValue)
                                * deltaNormalizedY
                                / (lastNormalizedY - marge)
                            )
                    else:
                        if normalizedPos.y() >= (1.0 - marge):
                            self._floatValue = self._minimum
                        else:
                            self._floatValue -= (
                                (self._floatValue - self._minimum)
                                * deltaNormalizedY
                                / (1.0 - marge - lastNormalizedY)
                            )
                    self._setNumberValue(self._floatValue)

    def mousePressEvent(self, event):
        # if not self._useTouchScreen :
        if debug:
            print("mousePressEvent")
        self._disableDragUpDown = False
        self._mouseLastPos = (
            self._mouseBeginPos
        ) = (
            QtGui.QCursor.pos()
        )  # event.globalPos() pas la meme chose ! global position est relatif à la fenetre principale par l'ecran !
        if event.button() == QtCore.Qt.LeftButton:
            self._mouseMode = self._mode.mouse.pressLeft.press
            if not self.showPopupType(self._mouseMode, DOWN):
                self.press(globalPosition=self._mouseLastPos)
        else:
            mode = self._mode.mouse.pressRight.press
            if not isinstance(mode, int):
                midleUpPoint = self.mapToGlobal(
                    QtCore.QPoint(int(self.width() * 0.5), 0)
                )
                if self._mouseLastPos.x() < midleUpPoint.x():  # leftZone
                    mode = mode.leftZone
                else:
                    mode = mode.rightZone
            self._mouseMode = mode
            self.showPopupType(self._mouseMode, DOWN)

    def press(self, globalPosition):
        if self._readOnly:
            return
        # print("press")
        self.setFocus()  # sert à quoi
        self._valueEditing = True
        # self.valueEditing.emit(True)
        self._floatValue = self._value
        if self._text:
            if self._value != self._maximum or not self._checkable:
                self._setNumberValue(self._maximum)
                # self._checked  = True
            else:
                self._setNumberValue(self._minimum)
                # self._checked  = False
        elif self._items:
            if len(self._items) < 3:
                self.incrementValue(1)
            else:
                if self._checkable:
                    self._checked = not self._checked
                    # self.clicked.emit(self._checked)
                    self.update()
                    # if self._checked:
                    #    self.showPopupType(VALUES,DOWN)
                else:
                    self.showPopupType(VALUES, DOWN)
        else:
            self._setNumberValue(
                self.mapFromGlobalF(globalPosition).x()
                * (self._maximum - self._minimum)
                / self.size().width()
                + self._minimum
            )
        self.clicked.emit(True)
        self.pressed.emit()

    def mapFromGlobalF(self, point):
        if isinstance(point, QtCore.QPointF):
            pointInt = point.toPoint()
            return self.mapFromGlobal(pointInt) + (point - pointInt)
        else:
            return self.mapFromGlobal(point)

    def keyPressEvent(self, event):
        key = event.key()
        if key in self._methode_from_key:
            self._methode_from_key[event.key()]()

    def stepUp(self):
        if self._items:
            self.incrementValue(-self._trueSingleStep)
        else:
            self.incrementValue(self._trueSingleStep)

    def stepDown(self):
        if self._items:
            self.incrementValue(self._trueSingleStep)
        else:
            self.incrementValue(-self._trueSingleStep)

    def stepRight(self):
        self.incrementValue(self._trueSingleStep)

    def stepLeft(self):
        self.incrementValue(-self._trueSingleStep)

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        if self._items:
            self.incrementValue(-self._trueSingleStep * delta)
        else:
            self.incrementValue(self._trueSingleStep * delta)
        event.accept()

    def setCurrentText(self, text):  # existe dans Qt5 mais pas Q4
        if text is None:
            self.setCurrentIndex(-1)
            # print(text, " introuvable")
        else:
            i = self.findText(text)
            self.setCurrentIndex(i)
            # print(text,i)

    def showPopup(self, sens=None):
        self._visiblePopup = True
        self._popupSens = sens
        # https://stackoverflow.com/questions/10057140/how-to-make-qcombobox-popup-upwards
        app = QtWidgets.QApplication.instance()
        oldAnimationEffects = app.isEffectEnabled(QtCore.Qt.UI_AnimateCombo)
        app.setEffectEnabled(QtCore.Qt.UI_AnimateCombo, False)
        QtWidgets.QComboBox.showPopup(self)
        app.setEffectEnabled(QtCore.Qt.UI_AnimateCombo, oldAnimationEffects)

    def eventFilter(self, obj, event):
        eventType = event.type()
        if obj == self._listView:
            if debug:
                print("obj == self._listView ", eventNames[eventType])
            if eventType == QtCore.QEvent.Show:
                frame = self.findChild(QtWidgets.QFrame)
                screenSize = self.window().windowHandle().screen().size()
                # frame.resize(frame.width(),self._frameSize.height())
                frame.resize(
                    max(self._frameSize.width(), frame.width()),
                    self._frameSize.height(),
                )
                x = min(frame.x(), screenSize.width() - frame.width())
                if self._popupSens == UP:
                    # For some reason, the frame's geometry is GLOBAL, not relative to the QComboBox!
                    frame.move(
                        x,
                        max(
                            0,
                            self.mapToGlobal(QtCore.QPoint(0, 0)).y() - frame.height(),
                        ),
                    )
                    return True
                elif self._popupSens == DOWN:
                    leftDown = self.mapToGlobal(QtCore.QPoint(0, self.height()))
                    frame.move(
                        x, min(screenSize.height() - frame.height(), leftDown.y())
                    )
                    return True
        elif obj == self._listView.window():
            if debug:
                print("obj == self._listView.window() ", eventNames[eventType])
            # eviter qu'un drag sur ecran tactile ne déclanche en MouseButtonPress qui ferme le menu avec hidepopup
            if eventType in (
                QtCore.QEvent.MouseButtonPress,
                QtCore.QEvent.MouseButtonDblClick,
            ):  # ,QtCore.QEvent.MouseMove,QtCore.QEvent.Wheel) :
                if event.source() == QtCore.Qt.MouseEventSynthesizedBySystem:
                    return True
            # permetre ouverture menus alternatifs quand drague up sur controlUI correpsondant Ã  menu (qui s'est déjà  deroulé lors du clic de souris)
            if self._lastPopup == VALUES:
                # n'arrive pas a recuperer les touchUpdate avec self quand popup
                # ni a activer avec self._listView.viewport().setAttribute(QtCore.Qt.WA_AcceptTouchEvents,True) # permet de detecter un touch event
                # du coup les deux ligne dessous ne servent à rien .. et je suis obligé de bidouiller pour transformer un mouseMove en pseudo touchUpdate en passant un argument  toucheUpdateFromMouse = True
                if eventType == QtCore.QEvent.TouchUpdate:
                    self.event(event)
                elif eventType == QtCore.QEvent.MouseMove:
                    if event.source() == QtCore.Qt.MouseEventSynthesizedBySystem:
                        # touchEvent  = QtCore.QEvent.QToucheEvent() #trop galère de génenrer un touch event ? du coup j'ai préféré passer un argument à la methode self.event ...
                        self.event(event, toucheUpdateFromMouse=True)
                        return True
                    else:
                        self.mouseMoveEvent(event)
                        return True
        elif obj == self:
            if debug:
                print("obj == self ", eventNames[eventType])
            if eventType in (
                QtCore.QEvent.MouseButtonPress,
                QtCore.QEvent.MouseButtonDblClick,
                QtCore.QEvent.MouseButtonRelease,
                QtCore.QEvent.MouseMove,
                QtCore.QEvent.Wheel,
            ):
                if event.source() == QtCore.Qt.MouseEventSynthesizedBySystem:
                    event.ignore()
                    return True
        if (
            trackpadHack
            and eventType
            in (
                QtCore.QEvent.MouseButtonPress,
                QtCore.QEvent.MouseButtonDblClick,
                QtCore.QEvent.MouseButtonRelease,
                QtCore.QEvent.MouseMove,
                QtCore.QEvent.Wheel,
            )
            and event.source() != QtCore.Qt.MouseEventSynthesizedBySystem
        ):
            # Hack pour trackpad du macbook pro quand on fait un clic-droit et drag
            if eventType == QtCore.QEvent.MouseMove:
                if (
                    self._trackpadPressingLeft
                    and self._trackpadPressingRight
                    and event.buttons()
                    != (QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
                ):
                    event.buttons = lambda: (
                        QtCore.Qt.LeftButton | QtCore.Qt.RightButton
                    )
                elif (
                    self._trackpadPressingLeft
                    and event.buttons() != QtCore.Qt.LeftButton
                ):
                    event.buttons = lambda: QtCore.Qt.LeftButton
                elif (
                    self._trackpadPressingRight
                    and event.buttons() != QtCore.Qt.RightButton
                ):
                    event.buttons = lambda: QtCore.Qt.RightButton
            elif eventType in (
                QtCore.QEvent.MouseButtonPress,
                QtCore.QEvent.MouseButtonDblClick,
            ):
                if event.button() == QtCore.Qt.LeftButton:
                    if self._trackpadPressingRight:
                        self._trackpadLeftPressTimer.start()
                        self._lastLeftPressObjAndEvent = (obj, event)
                        return True
                    else:
                        self._trackpadPressingLeft = True
                if event.button() == QtCore.Qt.RightButton:
                    self._trackpadLeftReleaseTimer.stop()
                    if self._trackpadPressingRight:
                        return True
                    else:
                        self._trackpadPressingRight = True
            elif eventType == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton:
                    if not self._trackpadPressingLeft:
                        self._lastLeftReleaseObjAndEvent = (obj, event)
                        self._trackpadLeftReleaseTimer.start()
                        return True
                    else:
                        self._trackpadPressingLeft = False
                if event.button() == QtCore.Qt.RightButton:
                    if self._trackpadLeftPressTimer.isActive():
                        self._trackpadLeftPressTimer.stop()
                        return True
                    else:
                        self._trackpadPressingRight = False

        if obj == self._listView.viewport():
            if debug:
                print("obj == viewport ", eventNames[eventType])
            if eventType == QtCore.QEvent.MouseButtonRelease:
                QtCore.QTimer.singleShot(
                    0, self.hidePopup
                )  # le hidepopup est normalement appellé automatiquement, mais ne marche pas quand on clique rapidement et qu'on a un menu qui a été deplacé car trop grand et du coup passe au dessus du widget. Le single shot est necessaire, sinon il n'upadate pas la valeure sur celle selectionnée

        return False

    def trackpadSheduledRightRelease(self):
        # Hack pour trackpad du macbook pro quand on fait un clic-droit et drag
        if debug:
            print("trackpadSheduledRightRelease")
        self._trackpadPressingRight = False
        obj, event = self._lastLeftReleaseObjAndEvent
        if obj in (self, self._listView, self._listView.window()):
            oldButton = event.button
            event.button = (
                lambda: QtCore.Qt.RightButton
            )  # fou la merde pour les evenemnt suivant , car il semble recycler
            obj.mouseReleaseEvent(event)
            event.button = oldButton
        else:
            # la ligne obj.mouseReleaseEvent(event) ne marche pas quand on fait un release en relachant majeur après auréculaire sur un element de la liste ... rajouté lignes ci dessous
            index = self._listView.currentIndex().row()
            if self._lastPopup == CONTROLS:
                self.setControlName(self._controlNames[index])
            elif self._lastPopup == INCONTROLS:
                self.setInControlName(self._inControlNames[index])
            self.hidePopup()

    def trackpadSheduledLeftPress(self):
        # Hack pour trackpad du macbook pro quand on fait un clic-droit et drag
        self._trackpadPressingLeft = True
        obj, event = self._lastLeftPressObjAndEvent
        obj.mouseReleaseEvent(event)

    def showPopupType(self, mode, sens=None):
        if mode == VALUES and self._items:
            if self._lastPopup != mode:
                if self._visiblePopup:
                    self.hidePopup()
                self._lastPopup = mode
                self.setPopItems(self._items)
                if self._value is not None:
                    self.blockSignals(True)
                    self.setCurrentIndex(self._value)
                    self.blockSignals(False)
                if debug:
                    print("show VALUES")
            self.showPopup(sens)
            return True
        elif mode == CONTROLS and self._controlNames:
            if self._lastPopup != mode:
                if self._visiblePopup:
                    self.hidePopup()
                self._lastPopup = mode
                self.setPopItems(self._controlNames)
                self.blockSignals(True)
                self.setCurrentText(self._controlName)
                self.blockSignals(False)
            if debug:
                print("show CONTROLS")
            self.showPopup(sens)
            return True
        elif mode == INCONTROLS and self._inControlNames:
            if self._lastPopup != mode:
                if self._visiblePopup:
                    self.hidePopup()
                self._lastPopup = mode
                self.setPopItems(self._inControlNames)
            self.blockSignals(True)
            if self._inControlName:
                self.setCurrentText(self._inControlName)
            else:
                self.setCurrentIndex(-1)
            self.blockSignals(False)
            self.showPopup(sens)
            if debug:
                print("show INCONTROLS")
            return True
        return False

    def hidePopup(self):
        """filtre si self._useTouchScreen pour eviter que la sortie vers le bas du widget avec le touché ne déclanche un hidePopup, par je ne sait quel bug oscure bug de Qt. J'ai du rajouter un un hidePopup qui lui cache le popup dans touts les cas"""
        if self._visiblePopup:
            if debug:
                print("hidePopup")
            self._visiblePopup = False
            QtWidgets.QComboBox.hidePopup(self)
            # permet de relacher un bouton non checkable , meme si on a commencer à afficher un popup par erreure en glissant vers le bas . Par exemple avec un tap tempo:
            self.release()

    def mouseReleaseEvent(self, event):
        # if not self._useTouchScreen :
        if debug:
            print("mouseReleaseEvent")
        if event.button() == QtCore.Qt.LeftButton:
            self.release(event.button())
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            if self._visiblePopup:
                QtCore.QTimer.singleShot(
                    1, self.hidePopup
                )  # j'ai l'impression que ça n'arrive jamais et qu'on peut effacer ces deux lignes

    def release(self, button=QtCore.Qt.LeftButton):
        if self._readOnly:
            return
        if self._text:
            if not self._checkable:
                self._setNumberValue(self._minimum)
        if not self._tracking:
            self._setValue(self._value)
        self._valueEditing = False
        # self.valueEditing.emit(False)
        self.clicked.emit(False)
        self.released.emit()

    def setSyncModule(self, value):
        self._sync.syncModule = value

    def getSyncModule(self):
        return self._sync.syncModule

    syncModule = QtCore.Property(str, getSyncModule, setSyncModule)

    def setSyncName(self, value):
        self._sync.syncName = value

    def getSyncName(self):
        return self._sync.syncName

    syncName = QtCore.Property(str, getSyncName, setSyncName)

    def setSyncSave(self, value):
        self._sync.save = value

    def getSyncSave(self):
        return self._sync.save

    syncSave = QtCore.Property(bool, getSyncSave, setSyncSave)

    # serialization

    def __getstate__(self):
        state = dict()
        if self._controlNames:
            state["controlName"] = self.controlName
        if self._inControlNames:
            state["inControlName"] = self.inControlName
        if self._text:
            state["value"] = self.value == self.maximum
        elif self._items:
            state["value"] = self._items[int(self.value)]
        else:
            state["value"] = self.value
        if self._controlNames and not self.controlName:
            del state["value"]
        return state

    @QtCore.Slot(bool)
    def setChecked(self, value, emit=True):  # pour compatibilité avec QPushButton
        if self._checked != value:
            self._checked = value
            if self._text:
                if value:
                    value = self._maximum
                else:
                    value = self._minimum
                self._setNumberValue(value, emit=emit)
            # else:
            #    self.clicked.emit(value)

    def getChecked(self):
        return self._checked

    checked = QtCore.Property(bool, getChecked, setChecked)

    @QtCore.Slot(bool)
    def setUnChecked(self, value, emit=True):  # pour compatibilité avec QPushButton
        self.setChecked(not value)

    def setItem(self, value, emit=True):
        if self._items:
            if isinstance(value, str):
                if value in self._items:
                    value = self._items.index(value)
                elif value in self._itemsIndexFromValue:
                    value = self._itemsIndexFromValue[value]
                else:
                    return
            elif value in self._itemsIndexFromValue:
                value = self._itemsIndexFromValue[value]
        elif isinstance(value, str):
            raise Exception(
                "impossible de faire un setValue avec %s sans self._items" % value
            )
        self._setNumberValue(value, emit=emit)

    @QtCore.Slot()
    def nextItem(self):
        self.setCurrentIndex((self.currentIndex() + 1) % self.count())

    @QtCore.Slot()
    def prevItem(self):
        self.setCurrentIndex((self.currentIndex() - 1) % self.count())

    @QtCore.Slot(bool)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(str)
    def setValueWithoutEmit(self, value):
        self.setValue(value, emit=False)

    @QtCore.Slot(bool)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(str)
    @QtCore.Slot(object)
    def setValue(self, value, emit=True):
        # print(value)
        if self._valueEditing:
            return
        self._setValue(value, emit=emit)

    def _setValue(self, value, emit=True):
        if isinstance(value, bool):  # On peut
            self.setChecked(value, emit=emit)
        elif self._items:
            self.setItem(value, emit=emit)
        elif isinstance(value, str):
            raise Exception(
                "impossible de faire un setValue avec %s sans self._items" % value
            )
        else:
            self._setNumberValue(value, emit=emit)

    # IL FAUT LE LESSER A LA FIN CAR QT DESIGNER INITIALIZE LESS DANS L'ORDRE DU CODE!! ET IL FAUT INITIALISATION APRES AVOIR REDEFINI MIN ET MAX !

    def _setNumberValue(self, value, fromSetInitValue=False, emit=True):
        if self._controlNames and not self._controlName:
            return
        if self._singleStep:
            value = (
                round((value - self.minimum) / self._trueSingleStep)
                * self._trueSingleStep
            ) + self.minimum
        value = round(
            value, self._trueDecimals
        )  # necessaire pour si single step 1.1 par exemple pour eventi d'avoir 3.3000000000000003
        if value <= self.minimum:
            value = self._minimum
        elif value >= self._maximum:
            value = self._maximum
        if not self._trueDecimals:
            value = int(value)
        if value != self._value or self._repeat:
            self._value = value
            outStr = None
            outBool = None
            outIntFloat = None
            outObject = None
            if (self._sendSetValue and not fromSetInitValue) or (
                self._sendInitValue and not self._initialized
            ):
                if self._text:
                    outBool = value == self._maximum
                    self._checked = outBool
                    outIntFloat = value
                    if outBool:
                        outStr = self._text
                elif self._items:
                    if self._itemsDict:
                        itemValue = self._itemsDict[self._items[value]]
                        if isinstance(
                            itemValue, bool
                        ):  # doit rester avant isinstance(itemValue,(int,float)) car un bool est un sous-classe de int
                            outBool = itemValue
                        elif isinstance(itemValue, (int, float)):
                            outIntFloat = itemValue
                        elif isinstance(itemValue, str):
                            outStr = itemValue
                        else:
                            outObject = itemValue
                    else:
                        outStr = self._items[value]
                else:
                    outIntFloat = value
            # ne pas remonter permet de dire qu'il ne faut plus initialiser si on a déjà initialisé avec deserialisation
            self._initialized = True
            if emit:  # and self._tracking:
                # self.emitValue()

                if outIntFloat is not None:
                    self.valueChanged[object].emit(outIntFloat)
                    self.valueChanged[float].emit(float(outIntFloat))
                    if isinstance(outIntFloat, int):
                        # print(outIntFloat)
                        self.valueChanged[int].emit(outIntFloat)
                if outBool is not None:
                    self.valueChanged[bool].emit(outBool)
                    self.valueChanged[object].emit(outBool)
                    # self.clicked.emit(outBool)
                if outStr is not None:
                    self.valueChanged[str].emit(outStr)
                    self.valueChanged[object].emit(outStr)
                if outObject is not None:
                    self.valueChanged[object].emit(outObject)
            if not self._text:
                self._contentText = None
            # permet de forcer rafraichissement, meme si le text n'a pas changé (ex tap tempo):
            self.update()

    def getContentText(self):
        if self._contentText is None:
            printedValue = value = self.value
            displayMinimum = self._displayMinimum
            displayMaximum = self._displayMaximum
            if (displayMinimum is not None) or (displayMaximum is not None):
                if displayMinimum is None:
                    displayMinimum = self._minimum
                if displayMaximum is None:
                    displayMaximum = self._maximum
                if not self._curve:
                    a = (displayMaximum - displayMinimum) / (
                        self._maximum - self._minimum
                    )
                    printedDecimals = max(
                        0, self._trueDecimals - math.floor(math.log10(abs(a)))
                    )
                    printedValue = round(
                        a * (value - self._minimum) + displayMinimum, printedDecimals
                    )
                    if (
                        printedValue == 0
                    ):  # permet de considerer -0.0 comme 0.0 (par exeple pour le input volume en dB dans SmartFace)
                        printedValue = 0.0
                else:
                    raise Exception(
                        "ne sais pas encore gerer les curve dans ControlUi.pyw"
                    )
            else:
                printedDecimals = self._trueDecimals
            if self._items:
                if self._prefix:
                    self._contentText = (
                        f"{self._prefix} {self._items[value]}{self._suffixWithSpace}"
                    )
                else:
                    self._contentText = f"{self._items[value]}{self._suffixWithSpace}"
            elif not self._text:
                prefix = self._prefix
                space = self.getPrefixSpace(printedValue)
                if self._istime:
                    minutes, seconds = divmod(int(printedValue), 60)
                    hours, minutes = divmod(minutes, 60)
                    if hours:
                        self._contentText = f"{hours}:{minutes:02}:{seconds:02}"
                    else:
                        self._contentText = f"{minutes}:{seconds:02}"

                elif isinstance(printedValue, float):
                    value_text = str(printedValue)
                    integer_part, decimal_part = value_text.split(".")
                    self._contentText = f"{prefix}{space}{integer_part}.{decimal_part:0<{printedDecimals}}{self._suffixWithSpace}"
                else:
                    self._contentText = (
                        f"{prefix}{space}{printedValue}{self._suffixWithSpace}"
                    )

        return self._contentText

    def updateMaxDigit(self):
        displayMinimum = self.displayMinimum
        if displayMinimum is None:
            displayMinimum = self.minimum
        displayMaximum = self.displayMaximum
        if displayMaximum is None:
            displayMaximum = self.maximum
        self._max_digits = max(
            len(f"{abs(displayMinimum)}".split(".")[0]),
            len(f"{abs(displayMaximum)}".split(".")[0]),
        )

    def getPrefixSpace(self, printedValue):
        # if printedValue > 0:
        #    digits = int(math.log10(printedValue))+1
        # elif printedValue == 0:
        #    digits = 1
        # else:
        #    digits = int(math.log10(-n))+1  # +1 if you don't count the '-'
        printedValueStr = f"{abs(printedValue)}"
        digits = printedValueStr.find(".")
        if digits == -1:
            digits = len(printedValueStr)
        space_padding = "\u2000" * (self._max_digits - digits)

        if self._prefix:
            if self._displayMinimum is not None:
                if self._displayMinimum < 0:
                    if printedValue < 0:
                        return space_padding + "\u2009"
                    return space_padding + "\u2000"
                return space_padding + " "
            elif self._minimum < 0:
                if printedValue < 0:
                    return space_padding + "\u2009"
                return space_padding + "\u2000"
            return space_padding + " "
        return ""

    def getMaxPrintedWidth(self):
        if self._maxPrintedWidth is None:
            space = ""
            fm = QtGui.QFontMetrics(self.font())
            printedValueMaximumWidth = 0
            if self._items:
                printedValueMaximumWidth = max([fm.width(item) for item in self._items])
            elif self._text:
                printedValueMaximumWidth = fm.width(self._text)
            else:
                if (
                    self._displayMinimum is not None
                    and self._displayMaximum is not None
                ):
                    displayMinimum = self._displayMinimum
                    displayMaximum = self._displayMaximum
                    a = (self._displayMaximum - self._displayMinimum) / (
                        self._maximum - self._minimum
                    )
                    printedDecimals = self._trueDecimals - min(
                        math.floor(math.log10(abs(a))), 0
                    )
                else:
                    displayMinimum = self._minimum
                    displayMaximum = self._maximum
                    printedDecimals = self._trueDecimals
                if not printedDecimals:
                    printedValueMaximumWidth = max(
                        [
                            fm.width(str(int(value)))
                            for value in (displayMinimum, displayMaximum)
                        ]
                    )
                else:
                    epsilon = 10 ** (-printedDecimals)
                    printedValueMaximumWidth = max(
                        [
                            fm.width(str(value))
                            for value in (
                                displayMinimum,
                                displayMinimum + epsilon,
                                displayMaximum - epsilon,
                                displayMaximum,
                            )
                        ]
                    )
                if self._prefix:
                    if displayMinimum < 0:
                        space = "\u2000"
                    else:
                        space = " "
            self._maxPrintedWidth = printedValueMaximumWidth + fm.width(
                f"{self._prefix}{space}{self._suffixWithSpace}"
            )
            if self._controlShortName:
                self._maxPrintedWidth += fm.width(self._controlShortName + " ")
        return self._maxPrintedWidth
        # fm = QtGui.QFontMetrics(self.font())
        # fm.width(elt)

    def getValue(self):
        if self._value is not None:
            return self._value
        else:
            return (
                self._initValue
            )  # permet d'eviter à Qt designer de planter , car il essaye de lire self.getValue, avant que le singleshot n'ai pu initialiser self._value à autre chose que None

    value = QtCore.Property(float, getValue, setValue)

    @QtCore.Slot(bool)
    def setCheckable(self, b):
        self._checkable = b

    def getCheckable(self):
        return self._checkable

    checkable = QtCore.Property(bool, getCheckable, setCheckable)

    def updatePopUpSelectedItem(self, i):
        # print("setContentText")
        if i != -1:
            if self._lastPopup == VALUES:
                self._setNumberValue(i)
            elif self._lastPopup == CONTROLS:
                self.setControlName(self.currentText())
            elif self._lastPopup == INCONTROLS:
                self.setInControlName(self.currentText())

    def setAlignment(self, b):
        self._alignment = b
        self.update()

    def getAlignment(self):
        return self._alignment

    alignment = QtCore.Property(QtCore.Qt.AlignmentFlag, getAlignment, setAlignment)

    # pour compatibilité avec anciennes boites de nombre:
    """def setButtonSymbols(self,b): 
        self._alignment = b
    def getButtonSymbols(self):
        return self._alignment
    buttonSymbols = QtCore.Property(bool, getButtonSymbols, setButtonSymbols)"""

    def setIndent(self, indent):
        self._indent = indent
        self.update()

    def getIndent(self):
        return self._indent

    indent = QtCore.Property(
        int, getIndent, setIndent
    )  # rajouté pour eviter que mon compilateur ne crée de property lui meme  (car pas defini de get?)

    def setBarFillColor(self, color):
        self._barFillColor = QColor(color)
        self.update()

    def getBarFillColor(self):
        if self._barFillColor is not None:
            return self._barFillColor
        else:
            barBorderColor = QtGui.QColor(self._barBorderColor)
            barBorderColor.setAlphaF(0.4)
            return barBorderColor

    barFillColor = QtCore.Property(QtGui.QColor, getBarFillColor, setBarFillColor)

    def setBarBorderColor(self, color):
        self._barBorderColor = QColor(color)
        self.update()

    def getBarBorderColor(self):
        return self._barBorderColor

    barBorderColor = QtCore.Property(QtGui.QColor, getBarBorderColor, setBarBorderColor)

    def setBorderColor(self, color):
        self._borderColor = QColor(color)
        self.update()

    def getBorderColor(self):
        return self._borderColor

    borderColor = QtCore.Property(QtGui.QColor, getBorderColor, setBorderColor)

    def setBorderDraw(self, b):
        self._borderDraw = b
        self.update()

    def getBorderDraw(self):
        return self._borderDraw

    borderDraw = QtCore.Property(bool, getBorderDraw, setBorderDraw)

    def setFill(self, b):
        self._fill = b
        self.update()

    def getFill(self):
        return self._fill

    fill = QtCore.Property(bool, getFill, setFill)

    def setFillColor(self, color):
        self._fillColor = QColor(color)
        self.update()

    def getFillColor(self):
        return self._fillColor

    fillColor = QtCore.Property(QtGui.QColor, getFillColor, setFillColor)

    @QtCore.Slot(bool)
    def setBorderBack(self, b):
        self._borderBack = b
        self.update()

    def getBorderBack(self):
        return self._borderBack

    borderBack = QtCore.Property(bool, getBorderBack, setBorderBack)

    @QtCore.Slot(bool)
    def setCornerRadius(self, b):
        self._cornerRadius = b
        self.update()

    def getCornerRadius(self):
        return self._cornerRadius

    cornerRadius = QtCore.Property(bool, getCornerRadius, setCornerRadius)

    def setPenWidth(self, width):
        self._penWidth = width
        self.update()

    def getPenWidth(self):
        return self._penWidth

    penWidth = QtCore.Property(float, getPenWidth, setPenWidth)

    def paintEvent(self, event):
        # print("paintEvent")
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        penWidth = self._penWidth
        halfPenWidth = penWidth / 2
        scaledCornerRadius = scaled(self._cornerRadius)
        scaledDiameter = scaledCornerRadius * 2
        pen = QtGui.QPen()
        pen.setWidthF(penWidth)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        rect = QtCore.QRectF(self.rect())
        width = rect.width()
        height = rect.height()
        insideRect = rect.adjusted(
            halfPenWidth, halfPenWidth, -halfPenWidth, -halfPenWidth
        )
        pixel_perfect_border = False
        if self._borderDraw and self._borderBack:
            pen.setColor(self._borderColor)
            painter.setPen(pen)
            if pixel_perfect_border:
                path = QtGui.QPainterPath()
                path.addRoundedRect(
                    penWidth,
                    penWidth,
                    width - 2 * penWidth,
                    height - 2 * penWidth,
                    scaledCornerRadius - penWidth,
                    scaledCornerRadius - penWidth,
                )
                painter.fillPath(path, self.fillColor)
            else:
                painter.setBrush(self.fillColor)
            painter.drawRoundedRect(
                QtCore.QRectF(
                    halfPenWidth,
                    halfPenWidth,
                    width - halfPenWidth,
                    height - halfPenWidth,
                ),
                scaledCornerRadius - halfPenWidth,
                scaledCornerRadius - halfPenWidth,
            )
        elif self._fill:
            path = QtGui.QPainterPath()
            path.addRoundedRect(
                # rect, scaledCornerRadius+halfPenWidth, scaledCornerRadius+halfPenWidth)
                rect,
                scaledCornerRadius,
                scaledCornerRadius,
            )

            painter.fillPath(path, self.fillColor)
        normalizedValue = 0
        if (self._value is not None) and (
            (not self._items)
            or "On" in self._items
            or "Play" in self._items
            or self._checkable
        ):  # and (not self._prefix)
            if self._checkable and (self._items or self._text):
                normalizedValue = self._checked
            else:
                normalizedValue = (self._value - self._minimum) / (
                    self._maximum - self._minimum
                )
        if normalizedValue > 0:
            pen.setColor(self._barBorderColor)
            painter.setPen(pen)
            value_width = width * normalizedValue
            path = QtGui.QPainterPath()
            if value_width <= 2 * penWidth:
                degrees = math.degrees(
                    math.acos(1.0 - (value_width / scaledCornerRadius))
                )
                path.moveTo(0, height / 2)
                path.arcTo(
                    0,
                    height - scaledDiameter,
                    scaledDiameter,
                    scaledDiameter,
                    180,
                    degrees,
                )
                path.arcTo(0, 0, scaledDiameter, scaledDiameter, 180 - degrees, degrees)
                path.closeSubpath()
                painter.fillPath(path, self._barBorderColor)
                # painter.drawPath(path)
            else:
                if value_width < (scaledCornerRadius + halfPenWidth):
                    radians = math.acos(
                        1.0
                        - (
                            (value_width - penWidth)
                            / (scaledCornerRadius - halfPenWidth)
                        )
                    )
                    degrees = math.degrees(radians)
                    path.moveTo(halfPenWidth, scaledCornerRadius)
                    path.arcTo(
                        halfPenWidth,
                        height - scaledDiameter + halfPenWidth,
                        scaledDiameter - penWidth,
                        scaledDiameter - penWidth,
                        180,
                        degrees,
                    )
                    path.arcTo(
                        halfPenWidth,
                        halfPenWidth,
                        scaledDiameter - penWidth,
                        scaledDiameter - penWidth,
                        180 - degrees,
                        degrees,
                    )
                    path.closeSubpath()
                    # painter.drawPath(path)
                else:
                    # path.moveTo(0, height/2)
                    path.moveTo(scaledCornerRadius, halfPenWidth)
                    path.arcTo(
                        halfPenWidth,
                        halfPenWidth,
                        scaledDiameter - penWidth,
                        scaledDiameter - penWidth,
                        90,
                        90,
                    )
                    path.arcTo(
                        halfPenWidth,
                        height - scaledDiameter + halfPenWidth,
                        scaledDiameter - penWidth,
                        scaledDiameter - penWidth,
                        180,
                        90,
                    )

                    # if value_width < width-(scaledDiameter+halfPenWidth):
                    if value_width <= (width - scaledCornerRadius + halfPenWidth):
                        path.lineTo(value_width - halfPenWidth, height - halfPenWidth)
                        path.lineTo(value_width - halfPenWidth, halfPenWidth)
                    else:
                        radians = math.acos(
                            1.0
                            - (width - value_width)
                            / (scaledCornerRadius - halfPenWidth)
                        )
                        degrees = math.degrees(radians)
                        path.arcTo(
                            width - scaledDiameter + halfPenWidth,
                            height - scaledDiameter + halfPenWidth,
                            scaledDiameter - penWidth,
                            scaledDiameter - penWidth,
                            -90,
                            90 - degrees,
                        )
                        path.arcTo(
                            width - scaledDiameter + halfPenWidth,
                            halfPenWidth,
                            scaledDiameter - penWidth,
                            scaledDiameter - penWidth,
                            degrees,
                            90 - degrees,
                        )
                path.closeSubpath()
                painter.fillPath(path, self.barFillColor)
                painter.drawPath(path)

            # path = QtGui.QPainterPath()
            # pen.setColor(self._borderColor)
            # painter.setPen(pen)
            # path.addRoundedRect(penWidth, penWidth, width-2*penWidth,
            #                    height-2*penWidth, scaledCornerRadius-penWidth, scaledCornerRadius-penWidth)
            # painter.fillPath(path, self.fillColor)
            # painter.drawRoundedRect(halfPenWidth, halfPenWidth, width-penWidth,
            #                       height-penWidth, scaledCornerRadius-halfPenWidth, scaledCornerRadius-halfPenWidth)

            # path.arcTo(halfPenWidth, halfPenWidth,
            #           scaledDiameter, scaledDiameter, 180, 90)

            # path.arcTo(halfPenWidth, halfPenWidth,
            #           scaledDiameter, scaledDiameter, 90, 0)

            # path.arcTo(halfPenWidth, halfPenWidth,
            #           scaledDiameter, scaledDiameter, 0, 90)

            # path.addRoundedRect(
            #    insideRect_value, scaledCornerRadius, scaledCornerRadius)
            # painter.fillPath(path, self.barFillColor)
            # pen.setColor(self._barBorderColor)
            # painter.setPen(pen)
            # painter.drawPath(path)
        if self._borderDraw and not self._borderBack:
            pen.setColor(self._borderColor)
            painter.setPen(pen)
            painter.drawRoundedRect(insideRect, scaledCornerRadius, scaledCornerRadius)

        # QtWidgets.QLabel.paintEvent(self,event)
        # inspired by https://code.woboq.org/qt5/qtbase/src/widgets/widgets/qlabel.cpp.html#_ZN6QLabel11changeEventEP6QEvent
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        if self._controlShortName:
            text = self._controlShortName + " " + self.getContentText()
        else:
            text = self.getContentText()

        # if self._inControlName:
        #    text = text +" ◄ " + self._inControlName
        self.style().drawItemText(
            painter,
            self.contentsRectWithMarging(self.alignment),
            self.alignment,
            opt.palette,
            self.isEnabled(),
            text,
            self.foregroundRole(),
        )
        if self._inControlName:
            # text = self._inControlName  + " ► " + text

            text = "◄ " + self._inControlName
            contentsRect = self.contentsRect()
            alignment = (
                QtCore.Qt.AlignVCenter
            )  # QtCore.Qt.AlignLeft| QtCore.Qt.AlignVCenter

            if bool(alignment & QtCore.Qt.AlignLeft):
                contentsRect.setLeft(
                    contentsRect.left() + self.getMaxPrintedWidth() + self._spaceWidth
                )
            else:
                fm = QtGui.QFontMetrics(self.font())
                textWidth = fm.width(text)
                halfWidth = 0.5 * (contentsRect.width())
                maxPrintedWidth = self.getMaxPrintedWidth()
                if (
                    maxPrintedWidth + self._spaceWidth > halfWidth
                    or maxPrintedWidth + self._spaceWidth + textWidth
                    > contentsRect.width()
                ):
                    left = maxPrintedWidth + self._spaceWidth
                elif textWidth > halfWidth:
                    left = contentsRect.right() - textWidth
                else:
                    left = halfWidth
                contentsRect.setLeft(left)
            # painter.setPen(QtGui.QColor(255,0,0))
            # painter.drawText(contentsRect,alignment, text)
            self.style().drawItemText(
                painter,
                contentsRect,
                alignment,
                opt.palette,
                self.isEnabled(),
                text,
                self.foregroundRole(),
            )

    def contentsRectWithMarging(self, alignement):
        contentsRect = self.contentsRect()
        if self.indent:
            if alignement & QtCore.Qt.AlignLeft:
                contentsRect.setLeft(contentsRect.left() + self.indent)
            if alignement & QtCore.Qt.AlignRight:
                contentsRect.setRight(contentsRect.right() - self.indent)
            if alignement & QtCore.Qt.AlignTop:
                contentsRect.setTop(contentsRect.top() + self.indent)
            if alignement & QtCore.Qt.AlignBottom:
                contentsRect.setBottom(contentsRect.bottom() - self.indent)
        return contentsRect

    @QtCore.Slot(object)
    def setControlNames(self, controlNames):
        if controlNames:
            self._controlNames = controlNames + [""]
        else:
            self._controlNames = None

    @QtCore.Slot(str)
    def setControlName(self, controlName):
        self._maxPrintedWidth = None
        self._controlShortName = self._controlName = controlName
        if controlName is None:
            self.setParameters(None)
            self._initialized = True
        self.outControlName.emit(controlName)
        # self.update()

    def getControlName(self):
        return self._controlName

    controlName = QtCore.Property(str, getControlName, setControlName)

    @QtCore.Slot(object)
    def setInControlNames(self, inControlNames):
        if inControlNames:
            self._inControlNames = inControlNames + [""]
        else:
            self._inControlNames = None

    @QtCore.Slot(str)
    def setInControlName(self, inControlName):
        self._inControlName = inControlName
        self.outInControlName.emit(inControlName)
        self.update()

    def getInControlName(self):
        return self._inControlName

    inControlName = QtCore.Property(str, getInControlName, setInControlName)


if __name__ == "__main__":
    import sys
    from SmartFramework.events.PrintSignal import PrintSignal

    # from parse import parse
    # debug = True
    # app = DebugdApp(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    app.setEffectEnabled(QtCore.Qt.UI_AnimateCombo, False)
    inControlNames = [
        "bouche ouvert",
        "sourire",
        "control3",
        "control4",
        "control5",
        "control6",
        "control7",
        "control8",
        "control9",
        "control10",
        "control11",
        "control12",
        "control13",
        "control14",
        "control15",
        "control16",
        "control17",
        "control18",
        "control3",
        "control4",
        "control5",
        "control6",
        "control7",
        "control8",
        "control9",
        "control10",
        "control11",
        "control12",
        "control13",
        "control14",
        "control15",
        "control16",
        "control17",
        "control18",
    ]
    controlNames = (
        []
    )  # "wahwah frequency","wahwah resonnance","control3","control4","control5","control6","control7","control8","control9","control10","control11","control12","control13","control14","control15","control16","control17","control18","control3","control4","control5","control6","control7","control8","control9","control10","control11","control12","control13","control14","control15","control16","control17","control18"]
    items = {
        "Whammi \u25B22OCT": 1,
        "Whammi \u25B2OCT": 2,
        "Whammi \u25B25TH": 3,
        "Whammi \u25B24TH": 4,
        "Whammi \u25BC2ND": 5,
        "Whammi \u25BC4TH": 6,
        "Whammi \u25BC5TH": 7,
        "Whammi \u25BCOCT": 8,
        "Whammi \u25BC2OCT": 9,
        "Whammi DIVE BOMB": 10,
        "Detune DEEP": 11,
        "Detune SHALLOW": 12,
        "Harmoni \u25BCOCT\u25B2OCT": 21,
        "Harmoni \u25BC5TH\u25B24TH": 20,
        "Harmoni \u25BC4TH\u25B23RD": 19,
        "Harmoni \u25BC5TH\u25B27TH": 18,
        "Harmoni \u25BC5TH\u25B26TH": 17,
        "Harmoni \u25BC4TH\u25B25TH": 16,
        "Harmoni \u25BC3RD\u25B24TH": 15,
        "Harmoni \u25BC3RD\u25B23RD": 14,
        "Harmoni \u25BC2ND\u25B23RD": 13,
    }

    main_widget = QtWidgets.QWidget()
    layout = QtWidgets.QGridLayout()
    main_widget.setLayout(layout)
    printSignal = PrintSignal()

    styleParameters = dict(
        alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
        borderDraw=True,
        borderColor=(50, 50, 50, 255),
        barBorderColor=(50, 255, 50, 0),
        barFillColor=(120, 220, 80, 255),
    )

    # #maximum = 128,value = 100,frame  = False, wrapping  = True)
    # widget_ControlUI_DoubleSpinBox3 = ControlUI(minimum = 0.0)
    # widget_QSpinBox = QtWidgets.QSpinBox(maximum = 128,value = 100, prefix = "prefix", suffix = "suffix", singleStep = 2)
    # widget_ControlUI_SpinBox = ControlUI(maximum = 128,value = 100, prefix = "prefix", suffix = "suffix", singleStep = 2)
    # widget_QDateTimeEdit = QtWidgets.QDateTimeEdit()
    # widget_Slider_int = ControlUI()#inControlNames = inControlNames,controlNames = controlNames)
    # widget_Slider_int_inControls = ControlUI(inControlNames = inControlNames, inControlName = "bouche ouvert")

    # ControlUI_checkable = ControlUI(checkable = True) A REVOIR
    # menu = QtWidgets.QMenu("menu")
    # menu.addSection("section")
    # menu.addAction("action1")
    # QPushButton_menu.setMenu(menu)

    # PushButton_1 = ControlUI(clickable = True)
    # PushButton_2 = ControlUI(text ="", clickable = True)
    # PushButton_3 = ControlUI(text ="clickable", clickable = True)
    # ControlUI_two_items_2 = ControlUI(items= {"Off" : False, "On" : True}, clickable = True)

    # ControlUI_two_items_5 = ControlUI(items= {"Off2" : False, "On1" : True}, clickable = True

    # ControlUI_two_items_8 = ControlUI(items= {"RECORD DIRECT TO DISK":0,"RECORD LAST 10 SEC" : 10}, clickable = True)

    # ControlUI_two_items_3 = ControlUI(items= {"Off" : False, "On" : True}, checkable = True))
    # ControlUI_two_items_6 = ControlUI(items= {"Off2" : False, "On1" : True}, checkable = True)
    # ControlUI_two_items_9 = ControlUI(items= {"RECORD DIRECT TO DISK":0,"RECORD LAST 10 SEC" : 10}, checkable = True)

    # ControlUI_three_itmes = ControlUI(items= items) #,inControlNames = inControlNames,controlNames = controlNames)
    # ControlUI_ComboBox_2 = ControlUI(items= items,inControlNames = inControlNames,controlNames = controlNames)

    # QProgressBar -> ControlUI

    # ControlUI_controls = ControlUI(controlNames = [
    # 				"RECORD DIRECT TO DISK",#
    # 				"RECORD LAST 10 SEC"], checkable = True) #,text ="text")
    # ControlUI_controls.setControlName("RECORD DIRECT TO DISK")
    # ControlUI_controlName = ControlUI(controlName ="controlName")

    # --- QSlider -> ControlUI

    widgetscode = """QProgressBar(maximum = 128,value = 100)
    ControlUI(readOnly = True,value = 100, displayMaximum = 100.0, suffix = "%")
    QProgressBar(maximum = 128,value = 100, format = "%v")
    ControlUI(readOnly = True,value = 100)
    QSlider(QtCore.Qt.Horizontal)
    ControlUI(maximum = 99)
    QSlider(QtCore.Qt.Horizontal, tracking = False)
    ControlUI(maximum = 99, tracking = False)
    QSpinBox()
    ControlUI()
    QDoubleSpinBox()
    ControlUI(decimals = 2)
    QDoubleSpinBox(singleStep = 0.1)
    ControlUI(singleStep = 0.1)
    ControlUI(displayMinimum = -15 ,displayMaximum = 4, suffix = "dB")
    QPushButton()
    ControlUI(text =" ")
    QPushButton(text = "text")
    ControlUI(text ="text")
    QPushButton(checkable = True)
    ControlUI(text = " ", checkable = True)
    QPushButton(text = "text", checkable = True)
    ControlUI(text = "text", checkable = True)
    QCheckBox(text = "text")
    ControlUI(text = "text", checkable = True)
    QCheckBox(text = "text", tristate = True)
    ControlUI(items= {"none" : 0, "selected":1 ,"all" : 2})
    ControlUI(items= {"Off" : False, "On" : True})
    ControlUI(items= {"Off2" : False, "On1" : True})
    ControlUI(items= {"zero":0,"ten" : 10})
    QComboBox();widget.addItems(["A","B","C","D"])
    ControlUI(items= ["A","B","C","D"])
    
    
    
    """

    for widget_code in widgetscode.splitlines():
        widget_code = widget_code.strip()
        if not widget_code:
            continue
        # print(widget_code)
        widget_code_splited = widget_code.split(";")
        widget = eval(widget_code_splited[0])
        if len(widget_code_splited) > 1:
            for elt in widget_code_splited[1:]:
                exec(elt)
        if widget_code.startswith("ControlUI"):
            colonne_name = 3
            colonne_widget = 2
            row = layout.rowCount() - 1
            if layout.itemAtPosition(row, colonne_widget):
                row += 1
        else:
            colonne_name = 0
            colonne_widget = 1
            row = layout.rowCount()
        widget.setObjectName(widget_code)
        layout.addWidget(QtWidgets.QLabel(text=widget_code), row, colonne_name)
        layout.addWidget(widget, row, colonne_widget)

        # class_ = widget.__class__
        # for base_class in class_.__mro__:
        #    for key, value in base_class.__dict__.items():
        #        print(key, value)
        moTest = widget.metaObject()
        for methodIdx in range(moTest.methodCount()):  # moTest.methodOffset()
            mmTest = moTest.method(methodIdx)
            if mmTest.methodType() == QtCore.QMetaMethod.Signal:
                signal_signature = bytes(mmTest.methodSignature()).decode("utf-8")
                if signal_signature not in [
                    "destroyed(QObject*)",
                    "destroyed()",
                    "objectNameChanged(QString)",
                    "windowTitleChanged(QString)",
                    "windowIconChanged(QIcon)",
                    "windowIconTextChanged(QString)",
                    "customContextMenuRequested(QPoint)",
                    "activated(int)",
                    "activated(QString)",
                    "highlighted(int)",
                    "highlighted(QString)",
                ]:
                    # QObject.connect(widget,SIGNAL(signal_signature),printSignal.input)
                    # signal_signature = signal_signature.replace("(","[").replace(")","]")
                    signal_name, signal_sig = signal_signature.split("(")
                    signal_sig = signal_sig[:-1]
                    if signal_sig:
                        qt_signal_sig_to_python_sig = {
                            "QString": "str",
                            "double": "float",
                            "PyQt_PyObject": "object",
                            "QDateTime": "QtCore.QDateTime",
                            "QTime": "QtCore.QTime",
                            "QDate": "QtCore.QDate",
                        }
                        if signal_sig in qt_signal_sig_to_python_sig:
                            signal_sig = qt_signal_sig_to_python_sig[signal_sig]
                        eval(f"widget.{signal_name}[{signal_sig}]").connect(
                            printSignal.input
                        )
                    else:
                        widget.__getattr__(signal_name).connect(printSignal.input)

    # widget2bis = ControlUI(items= {"Off2" : False, "On2" : True}, checkable = False,inControlNames = inControlNames,controlNames = controlNames)

    # widget3 = ControlUI(text ="Tap Tempo", checkable = False,inControlNames = inControlNames,controlNames = controlNames)
    # widget3 = ControlUI(text ="Tap Tempo", checkable = False,inControlNames = inControlNames,controlNames = controlNames)

    # widget3bis = ControlUI(text ="Tap Tempo", checkable = False,inControlNames = inControlNames,controlNames = controlNames)
    # widget2.valueChanged[bool].connect(widget2bis.setValue)

    main_widget.setMinimumWidth(800)
    main_widget.show()
    app.exec_()
