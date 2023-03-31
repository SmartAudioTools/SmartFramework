from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.Thread import Thread


TOOLTIP = "Thread"
DOM_XML = """
<ui language='c++'>
    <widget class='Thread' name='Thread'>
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
    Thread, module="Thread", tool_tip=TOOLTIP, xml=DOM_XML
)
