import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.video.VideoBuffer
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='VideoBuffer' name='VideoBuffer'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.video.VideoBuffer.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
VideoBuffer = transformClassForQtDesigner(SmartFramework.video.VideoBuffer.VideoBuffer)


def new_super(class_, inst, patched_class=VideoBuffer):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.video.VideoBuffer.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = VideoBuffer.__doc__ # pourra remetre quand bug corrigé
tool_tip = VideoBuffer.__new__(VideoBuffer).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    VideoBuffer,
    module="VideoBuffer",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.video",
    container=False,
)
