import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.ui.StdOutUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='StdOutUI' name='StdOutUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.ui.StdOutUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
StdOutUI = transformClassForQtDesigner(SmartFramework.ui.StdOutUI.StdOutUI)


def new_super(class_, inst, patched_class=StdOutUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.ui.StdOutUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = StdOutUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = StdOutUI.__new__(StdOutUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    StdOutUI,
    module="StdOutUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.ui",
    container=False,
)
