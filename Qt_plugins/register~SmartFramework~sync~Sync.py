import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.sync.Sync
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='Sync' name='Sync'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.sync.Sync.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
Sync = transformClassForQtDesigner(SmartFramework.sync.Sync.Sync)


def new_super(class_, inst, patched_class=Sync):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.sync.Sync.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = Sync.__doc__ # pourra remetre quand bug corrigé
tool_tip = Sync.__new__(Sync).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    Sync,
    module="Sync",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.sync",
    container=False,
)
