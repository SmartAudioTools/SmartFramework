from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiChannelSelect import MidiChannelSelect


TOOLTIP = "MidiChannelSelect"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiChannelSelect' name='MidiChannelSelect'>
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
    MidiChannelSelect, module="MidiChannelSelect", tool_tip=TOOLTIP, xml=DOM_XML
)
