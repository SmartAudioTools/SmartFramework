from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.ui.ColorUI import ColorUI


TOOLTIP = "ColorUI"
DOM_XML = """
<ui language='c++'>
    <widget class='ColorUI' name='ColorUI'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>400</width>
                <height>200</height>
            </rect>
        </property>
    </widget>
</ui>
"""

QPyDesignerCustomWidgetCollection.registerCustomWidget(
    ColorUI, module="ColorUI", tool_tip=TOOLTIP, xml=DOM_XML
)
