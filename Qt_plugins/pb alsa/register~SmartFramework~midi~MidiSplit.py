from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiSplit import MidiSplit


TOOLTIP = "MidiSplit"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiSplit' name='MidiSplit'>
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
    MidiSplit, module="MidiSplit", tool_tip=TOOLTIP, xml=DOM_XML
)
