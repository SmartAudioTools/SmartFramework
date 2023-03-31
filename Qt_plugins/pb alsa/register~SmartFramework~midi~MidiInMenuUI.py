from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiInMenuUI import MidiInMenuUI


TOOLTIP = "MidiInMenuUI"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiInMenuUI' name='MidiInMenuUI'>
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
    MidiInMenuUI, module="MidiInMenuUI", tool_tip=TOOLTIP, xml=DOM_XML
)
