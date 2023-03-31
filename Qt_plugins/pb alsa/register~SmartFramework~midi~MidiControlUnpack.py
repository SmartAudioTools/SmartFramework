from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiControlUnpack import MidiControlUnpack


TOOLTIP = "MidiControlUnpack"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiControlUnpack' name='MidiControlUnpack'>
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
    MidiControlUnpack, module="MidiControlUnpack", tool_tip=TOOLTIP, xml=DOM_XML
)
