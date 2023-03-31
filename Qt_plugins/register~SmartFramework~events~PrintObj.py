import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.events.PrintObj
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='PrintObj' name='PrintObj'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.events.PrintObj.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
PrintObj = transformClassForQtDesigner(SmartFramework.events.PrintObj.PrintObj)


def new_super(class_, inst, patched_class=PrintObj):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.events.PrintObj.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = PrintObj.__doc__ # pourra remetre quand bug corrigé
tool_tip = PrintObj.__new__(PrintObj).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    PrintObj,
    module="PrintObj",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.events",
    container=False,
)
