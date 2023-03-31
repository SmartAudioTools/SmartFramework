import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import SmartFramework.time.TestGranularityUI
from SmartFramework.designer import transformClassForQtDesigner


DOM_XML = """
<ui language='c++'>
    <widget class='TestGranularityUI' name='TestGranularityUI'>
    </widget>
</ui>
"""

icon = os.path.splitext(SmartFramework.time.TestGranularityUI.__file__)[0] + ".png"
if not os.path.exists(icon):
    icon = "/home/smartaudiotools/icones/Blank.png"

# hack pour permetre de rajouter interface graphique à un objet non graphique
TestGranularityUI = transformClassForQtDesigner(
    SmartFramework.time.TestGranularityUI.TestGranularityUI
)


def new_super(class_, inst, patched_class=TestGranularityUI):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)


SmartFramework.time.TestGranularityUI.super = new_super


# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
# tool_tip = TestGranularityUI.__doc__ # pourra remetre quand bug corrigé
tool_tip = TestGranularityUI.__new__(TestGranularityUI).__doc__
if tool_tip is None:
    tool_tip = ""


QPyDesignerCustomWidgetCollection.registerCustomWidget(
    TestGranularityUI,
    module="TestGranularityUI",
    tool_tip=tool_tip,
    xml=DOM_XML,
    icon=icon,
    group="SmartFramework.time",
    container=False,
)
