import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.events.Gate
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='Gate' name='Gate'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.events.Gate.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
Gate = transformClassForQtDesigner(SmartFramework.events.Gate.Gate)


def new_super(class_, inst, patched_class=Gate):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.events.Gate.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = Gate.__doc__ # pourra remetre quand bug corrigé
tool_tip = Gate.__new__(Gate).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    Gate,
    module="Gate",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.events",
    container=False,
)
