import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.video.VideoRecord
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='VideoRecord' name='VideoRecord'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.video.VideoRecord.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
VideoRecord = transformClassForQtDesigner(SmartFramework.video.VideoRecord.VideoRecord)


def new_super(class_, inst, patched_class=VideoRecord):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.video.VideoRecord.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = VideoRecord.__doc__ # pourra remetre quand bug corrigé
tool_tip = VideoRecord.__new__(VideoRecord).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    VideoRecord,
    module="VideoRecord",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.video",
    container=False,
)
