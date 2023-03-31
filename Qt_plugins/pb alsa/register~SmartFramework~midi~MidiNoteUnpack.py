from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiNoteUnpack import MidiNoteUnpack


TOOLTIP = "MidiNoteUnpack"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiNoteUnpack' name='MidiNoteUnpack'>
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
    MidiNoteUnpack, module="MidiNoteUnpack", tool_tip=TOOLTIP, xml=DOM_XML
)
