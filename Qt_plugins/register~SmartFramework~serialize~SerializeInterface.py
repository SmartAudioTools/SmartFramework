import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.serialize.SerializeInterface
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='SerializeInterface' name='SerializeInterface'>
    </widget>
</ui>
"""

icon = (
    os.path.splitext(SmartFramework.serialize.SerializeInterface.__file__)[0] + ".png"
)
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
SerializeInterface = transformClassForQtDesigner(
    SmartFramework.serialize.SerializeInterface.SerializeInterface
)


def new_super(class_, inst, patched_class=SerializeInterface):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.serialize.SerializeInterface.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = SerializeInterface.__doc__ # pourra remetre quand bug corrigé
tool_tip = SerializeInterface.__new__(SerializeInterface).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    SerializeInterface,
    module="SerializeInterface",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.serialize",
    container=False,
)
