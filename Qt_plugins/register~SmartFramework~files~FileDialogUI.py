import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.files.FileDialogUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='FileDialogUI' name='FileDialogUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.files.FileDialogUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
FileDialogUI = transformClassForQtDesigner(
    SmartFramework.files.FileDialogUI.FileDialogUI
)


def new_super(class_, inst, patched_class=FileDialogUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.files.FileDialogUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = FileDialogUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = FileDialogUI.__new__(FileDialogUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    FileDialogUI,
    module="FileDialogUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.files",
    container=False,
)
