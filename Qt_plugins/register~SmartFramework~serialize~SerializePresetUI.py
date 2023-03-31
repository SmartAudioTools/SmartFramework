import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.serialize.SerializePresetUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='SerializePresetUI' name='SerializePresetUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.serialize.SerializePresetUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
SerializePresetUI = transformClassForQtDesigner(
    SmartFramework.serialize.SerializePresetUI.SerializePresetUI
)


def new_super(class_, inst, patched_class=SerializePresetUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.serialize.SerializePresetUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = SerializePresetUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = SerializePresetUI.__new__(SerializePresetUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    SerializePresetUI,
    module="SerializePresetUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.serialize",
    container=False,
)
