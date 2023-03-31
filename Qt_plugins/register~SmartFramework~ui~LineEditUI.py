import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.ui.LineEditUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='LineEditUI' name='LineEditUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.ui.LineEditUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
LineEditUI = transformClassForQtDesigner(SmartFramework.ui.LineEditUI.LineEditUI)


def new_super(class_, inst, patched_class=LineEditUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.ui.LineEditUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = LineEditUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = LineEditUI.__new__(LineEditUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    LineEditUI,
    module="LineEditUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.ui",
    container=False,
)
