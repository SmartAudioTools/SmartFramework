import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.image.ImageShowUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='ImageShowUI' name='ImageShowUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.image.ImageShowUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
ImageShowUI = transformClassForQtDesigner(SmartFramework.image.ImageShowUI.ImageShowUI)


def new_super(class_, inst, patched_class=ImageShowUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.image.ImageShowUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = ImageShowUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = ImageShowUI.__new__(ImageShowUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    ImageShowUI,
    module="ImageShowUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.image",
    container=False,
)
