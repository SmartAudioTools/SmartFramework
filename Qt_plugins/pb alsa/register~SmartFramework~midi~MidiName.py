from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiName import MidiName


TOOLTIP = "MidiName"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiName' name='MidiName'>
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
    MidiName, module="MidiName", tool_tip=TOOLTIP, xml=DOM_XML
)
