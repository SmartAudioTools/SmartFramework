import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.video.VideoPlayerUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='VideoPlayerUI' name='VideoPlayerUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.video.VideoPlayerUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
VideoPlayerUI = transformClassForQtDesigner(
    SmartFramework.video.VideoPlayerUI.VideoPlayerUI
)


def new_super(class_, inst, patched_class=VideoPlayerUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.video.VideoPlayerUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = VideoPlayerUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = VideoPlayerUI.__new__(VideoPlayerUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    VideoPlayerUI,
    module="VideoPlayerUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.video",
    container=False,
)
