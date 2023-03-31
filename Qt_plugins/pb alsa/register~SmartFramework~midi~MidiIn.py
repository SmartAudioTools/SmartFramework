from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiIn import MidiIn


TOOLTIP = "MidiIn"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiIn' name='MidiIn'>
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
    MidiIn, module="MidiIn", tool_tip=TOOLTIP, xml=DOM_XML
)
