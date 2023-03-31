from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiNotePack import MidiNotePack


TOOLTIP = "MidiNotePack"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiNotePack' name='MidiNotePack'>
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
    MidiNotePack, module="MidiNotePack", tool_tip=TOOLTIP, xml=DOM_XML
)
