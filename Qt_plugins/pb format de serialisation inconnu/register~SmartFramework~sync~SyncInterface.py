from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.sync.SyncInterface import SyncInterface


TOOLTIP = "SyncInterface"
DOM_XML = """
<ui language='c++'>
    <widget class='SyncInterface' name='SyncInterface'>
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
    SyncInterface, module="SyncInterface", tool_tip=TOOLTIP, xml=DOM_XML
)
