from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiControlPack import MidiControlPack


TOOLTIP = "MidiControlPack"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiControlPack' name='MidiControlPack'>
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
    MidiControlPack, module="MidiControlPack", tool_tip=TOOLTIP, xml=DOM_XML
)
