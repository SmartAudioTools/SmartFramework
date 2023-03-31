import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.sync.Receive
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='Receive' name='Receive'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.sync.Receive.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
Receive = transformClassForQtDesigner(SmartFramework.sync.Receive.Receive)


def new_super(class_, inst, patched_class=Receive):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.sync.Receive.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = Receive.__doc__ # pourra remetre quand bug corrigé
tool_tip = Receive.__new__(Receive).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    Receive,
    module="Receive",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.sync",
    container=False,
)
