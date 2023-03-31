import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.ui.ListEditorUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='ListEditorUI' name='ListEditorUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.ui.ListEditorUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
ListEditorUI = transformClassForQtDesigner(SmartFramework.ui.ListEditorUI.ListEditorUI)


def new_super(class_, inst, patched_class=ListEditorUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.ui.ListEditorUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = ListEditorUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = ListEditorUI.__new__(ListEditorUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    ListEditorUI,
    module="ListEditorUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.ui",
    container=False,
)
