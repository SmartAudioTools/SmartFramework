import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
import SmartFramework.ui.CheckComboBoxUI
from SmartFramework.ui import exceptionDialog
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='CheckComboBoxUI' name='CheckComboBoxUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.ui.CheckComboBoxUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
CheckComboBoxUI = transformClassForQtDesigner(
    SmartFramework.ui.CheckComboBoxUI.CheckComboBoxUI
)


def new_super(class_, inst, patched_class=CheckComboBoxUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.ui.CheckComboBoxUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = CheckComboBoxUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = CheckComboBoxUI.__new__(CheckComboBoxUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    CheckComboBoxUI,
    module="CheckComboBoxUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.ui",
    container=False,
)
