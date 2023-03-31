from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiControlSelect import MidiControlSelect


TOOLTIP = "MidiControlSelect"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiControlSelect' name='MidiControlSelect'>
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
    MidiControlSelect, module="MidiControlSelect", tool_tip=TOOLTIP, xml=DOM_XML
)
