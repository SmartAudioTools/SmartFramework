import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.files.FileDialog
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='FileDialog' name='FileDialog'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.files.FileDialog.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
FileDialog = transformClassForQtDesigner(SmartFramework.files.FileDialog.FileDialog)


def new_super(class_, inst, patched_class=FileDialog):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.files.FileDialog.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = FileDialog.__doc__ # pourra remetre quand bug corrigé
tool_tip = FileDialog.__new__(FileDialog).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    FileDialog,
    module="FileDialog",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.files",
    container=False,
)
