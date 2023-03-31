import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.plot.CurveSelectorUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='CurveSelectorUI' name='CurveSelectorUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.plot.CurveSelectorUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
CurveSelectorUI = transformClassForQtDesigner(
    SmartFramework.plot.CurveSelectorUI.CurveSelectorUI
)


def new_super(class_, inst, patched_class=CurveSelectorUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.plot.CurveSelectorUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = CurveSelectorUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = CurveSelectorUI.__new__(CurveSelectorUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    CurveSelectorUI,
    module="CurveSelectorUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.plot",
    container=False,
)
