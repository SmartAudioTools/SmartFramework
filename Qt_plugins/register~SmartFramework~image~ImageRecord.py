import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.image.ImageRecord
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='ImageRecord' name='ImageRecord'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.image.ImageRecord.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
ImageRecord = transformClassForQtDesigner(SmartFramework.image.ImageRecord.ImageRecord)


def new_super(class_, inst, patched_class=ImageRecord):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.image.ImageRecord.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = ImageRecord.__doc__ # pourra remetre quand bug corrigé
tool_tip = ImageRecord.__new__(ImageRecord).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    ImageRecord,
    module="ImageRecord",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.image",
    container=False,
)
