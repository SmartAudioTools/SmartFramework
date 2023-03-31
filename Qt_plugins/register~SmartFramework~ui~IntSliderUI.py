import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.ui.IntSliderUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='IntSliderUI' name='IntSliderUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.ui.IntSliderUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
IntSliderUI = transformClassForQtDesigner(SmartFramework.ui.IntSliderUI.IntSliderUI)


def new_super(class_, inst, patched_class=IntSliderUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.ui.IntSliderUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = IntSliderUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = IntSliderUI.__new__(IntSliderUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    IntSliderUI,
    module="IntSliderUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.ui",
    container=False,
)
