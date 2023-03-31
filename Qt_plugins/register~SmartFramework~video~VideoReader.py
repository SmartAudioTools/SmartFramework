import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.video.VideoReader
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='VideoReader' name='VideoReader'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.video.VideoReader.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
VideoReader = transformClassForQtDesigner(SmartFramework.video.VideoReader.VideoReader)


def new_super(class_, inst, patched_class=VideoReader):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.video.VideoReader.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = VideoReader.__doc__ # pourra remetre quand bug corrigé
tool_tip = VideoReader.__new__(VideoReader).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    VideoReader,
    module="VideoReader",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.video",
    container=False,
)
