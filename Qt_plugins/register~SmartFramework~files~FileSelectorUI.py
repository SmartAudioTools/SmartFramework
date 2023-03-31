import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.files.FileSelectorUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='FileSelectorUI' name='FileSelectorUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.files.FileSelectorUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
FileSelectorUI = transformClassForQtDesigner(
    SmartFramework.files.FileSelectorUI.FileSelectorUI
)


def new_super(class_, inst, patched_class=FileSelectorUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.files.FileSelectorUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = FileSelectorUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = FileSelectorUI.__new__(FileSelectorUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    FileSelectorUI,
    module="FileSelectorUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.files",
    container=False,
)
