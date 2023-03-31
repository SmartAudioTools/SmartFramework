import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.events.ToQt
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='ToQt' name='ToQt'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.events.ToQt.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
ToQt = transformClassForQtDesigner(SmartFramework.events.ToQt.ToQt)


def new_super(class_, inst, patched_class=ToQt):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.events.ToQt.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = ToQt.__doc__ # pourra remetre quand bug corrigé
tool_tip = ToQt.__new__(ToQt).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    ToQt,
    module="ToQt",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.events",
    container=False,
)
