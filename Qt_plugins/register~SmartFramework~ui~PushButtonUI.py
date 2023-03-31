import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.ui.PushButtonUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='PushButtonUI' name='PushButtonUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.ui.PushButtonUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
PushButtonUI = transformClassForQtDesigner(SmartFramework.ui.PushButtonUI.PushButtonUI)


def new_super(class_, inst, patched_class=PushButtonUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.ui.PushButtonUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = PushButtonUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = PushButtonUI.__new__(PushButtonUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    PushButtonUI,
    module="PushButtonUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.ui",
    container=False,
)
