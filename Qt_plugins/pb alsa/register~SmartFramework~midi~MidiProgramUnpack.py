from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiProgramUnpack import MidiProgramUnpack


TOOLTIP = "MidiProgramUnpack"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiProgramUnpack' name='MidiProgramUnpack'>
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
    MidiProgramUnpack, module="MidiProgramUnpack", tool_tip=TOOLTIP, xml=DOM_XML
)
