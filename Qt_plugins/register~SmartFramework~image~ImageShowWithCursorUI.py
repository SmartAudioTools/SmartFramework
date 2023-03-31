import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.image.ImageShowWithCursorUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='ImageShowWithCursorUI' name='ImageShowWithCursorUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.image.ImageShowWithCursorUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
ImageShowWithCursorUI = transformClassForQtDesigner(
    SmartFramework.image.ImageShowWithCursorUI.ImageShowWithCursorUI
)


def new_super(class_, inst, patched_class=ImageShowWithCursorUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.image.ImageShowWithCursorUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = ImageShowWithCursorUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = ImageShowWithCursorUI.__new__(ImageShowWithCursorUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    ImageShowWithCursorUI,
    module="ImageShowWithCursorUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.image",
    container=False,
)
