import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.time.QtTimer
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='QtTimer' name='QtTimer'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.time.QtTimer.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
QtTimer = transformClassForQtDesigner(SmartFramework.time.QtTimer.QtTimer)


def new_super(class_, inst, patched_class=QtTimer):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.time.QtTimer.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = QtTimer.__doc__ # pourra remetre quand bug corrigé
tool_tip = QtTimer.__new__(QtTimer).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    QtTimer,
    module="QtTimer",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.time",
    container=False,
)
