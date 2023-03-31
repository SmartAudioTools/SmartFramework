from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.sync.SyncPresetUI import SyncPresetUI


TOOLTIP = "SyncPresetUI"
DOM_XML = """
<ui language='c++'>
    <widget class='SyncPresetUI' name='SyncPresetUI'>
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
    SyncPresetUI, module="SyncPresetUI", tool_tip=TOOLTIP, xml=DOM_XML
)
