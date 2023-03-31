import os
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui import exceptionDialog
import {module}
from SmartFramework.designer import transformClassForQtDesigner

                                     
DOM_XML = """
<ui language='c++'>
    <widget class='{module}' name='{Name}'>
    </widget>
</ui>
"""

icon = os.path.splitext({module}.__file__)[0]+'.png'
if  not os.path.exists(icon):
    icon = '/home/smartaudiotools/icones/Blank.png'

# hack pour permetre de rajouter interface graphique à un objet non graphique
{Name} = transformClassForQtDesigner({module}.{Name})
def new_super(class_, inst, patched_class  = {Name} ):
    if isinstance(inst, patched_class):
        return super(patched_class, inst)
    else:
        return super(class_, inst)
{module}.super = new_super 
    

# contourne bug de PySide6: https://bugreports.qt.io/browse/PYSIDE-1884
#tool_tip = {Name}.__doc__ # pourra remetre quand bug corrigé
tool_tip = {Name}.__new__({Name}).__doc__
if tool_tip is None :
    tool_tip = ""
        

QPyDesignerCustomWidgetCollection.registerCustomWidget(
    {Name}, 
    module="{module}",
    tool_tip=tool_tip, 
    xml=DOM_XML,
    icon=icon,
    group="{sub_package}",
    container=False
    )