import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.ui.TextEditorUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='TextEditorUI' name='TextEditorUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.ui.TextEditorUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
TextEditorUI = transformClassForQtDesigner(SmartFramework.ui.TextEditorUI.TextEditorUI)


def new_super(class_, inst, patched_class=TextEditorUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.ui.TextEditorUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = TextEditorUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = TextEditorUI.__new__(TextEditorUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    TextEditorUI,
    module="TextEditorUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.ui",
    container=False,
)
