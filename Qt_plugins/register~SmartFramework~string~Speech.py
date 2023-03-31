import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.string.Speech
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='Speech' name='Speech'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.string.Speech.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
Speech = transformClassForQtDesigner(SmartFramework.string.Speech.Speech)


def new_super(class_, inst, patched_class=Speech):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.string.Speech.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = Speech.__doc__ # pourra remetre quand bug corrigé
tool_tip = Speech.__new__(Speech).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    Speech,
    module="Speech",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.string",
    container=False,
)
