from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiProgramPack import MidiProgramPack


TOOLTIP = "MidiProgramPack"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiProgramPack' name='MidiProgramPack'>
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
    MidiProgramPack, module="MidiProgramPack", tool_tip=TOOLTIP, xml=DOM_XML
)
