﻿import os
import SmartFramework.video.VideoCodecMenuUI
from SmartFramework.designer import transformClassForQtDesigner
from qtpy import QtGui, QtDesigner
from SmartFramework.ui import exceptionDialog

os.environ["QT_API"] = "pyqt5"

VideoCodecMenuUI = transformClassForQtDesigner(
    SmartFramework.video.VideoCodecMenuUI.VideoCodecMenuUI
)
icon_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "VideoCodecMenuUI.png"
)
if os.path.exists(icon_path):
    VideoCodecMenuUI.__icon__ = QtGui.QIcon(icon_path)
else:
    VideoCodecMenuUI.__icon__ = QtGui.QIcon()


class VideoCodecMenuUIPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    # The __init__() method is only used to set up the plugin and define its initialized variable.
    def __init__(self, parent=None):
        super(VideoCodecMenuUIPlugin, self).__init__(parent)
        self.initialized = False

    # The initialize() and isInitialized() methods allow the plugin to set up any required resources, ensuring that this can only happen once for each plugin.
    def initialize(self, core):
        if self.initialized:
            return
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    # This factory method creates new instances of our custom widget with the appropriate parent.
    def createWidget(self, parent):
        # regle le problem du super(...,self) pour l'objet en question mais doit imédiatement defaire pour eviter de foutre la merde sur les autres qui vont l'utiliser
        old_class = SmartFramework.video.VideoCodecMenuUI.VideoCodecMenuUI
        SmartFramework.video.VideoCodecMenuUI.VideoCodecMenuUI = VideoCodecMenuUI
        instance = VideoCodecMenuUI(parent=parent)
        SmartFramework.video.VideoCodecMenuUI.VideoCodecMenuUI = old_class
        return instance

    # This method returns the name of the custom widget class that is provided by this plugin.
    def name(self):
        return "VideoCodecMenuUI"

    # Returns the name of the group in Qt Designer's widget box that this widget belongs to.
    def group(self):
        return "SmartFramework.video"

    # Returns the icon used to represent the custom widget in Qt Designer's widget box.
    def icon(self):
        return VideoCodecMenuUI.__icon__

    # Returns a short description of the custom widget for use in a tool tip.
    def toolTip(self):
        return VideoCodecMenuUI.__doc__

    # Returns a short description of the custom widget for use in a "What's This?" help message for the widget.
    def whatsThis(self):
        return VideoCodecMenuUI.__doc__

    # Returns True if the custom widget acts as a container for other widgets; otherwise returns False. Note that plugins for custom containers also need to provide an implementation of the QDesignerContainerExtension interface if they need to add custom editing support to Qt Designer.
    def isContainer(self):
        return False

    # Returns an XML description of a custom widget instance that describes default values for its properties. Each custom widget created by this plugin will be configured using this description.

    # Returns the module containing the custom widget class. It may include a module path.
    def includeFile(self):
        return "SmartFramework.video.VideoCodecMenuUI"
