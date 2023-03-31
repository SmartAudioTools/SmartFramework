from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.plot.PlotUI import PlotUI


TOOLTIP = "PlotUI"
DOM_XML = """
<ui language='c++'>
    <widget class='PlotUI' name='PlotUI'>
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
    PlotUI, module="PlotUI", tool_tip=TOOLTIP, xml=DOM_XML
)
