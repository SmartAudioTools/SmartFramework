from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiOut import MidiOut


TOOLTIP = "MidiOut"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiOut' name='MidiOut'>
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
    MidiOut, module="MidiOut", tool_tip=TOOLTIP, xml=DOM_XML
)
