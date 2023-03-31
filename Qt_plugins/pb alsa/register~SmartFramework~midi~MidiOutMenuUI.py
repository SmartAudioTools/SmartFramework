from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiOutMenuUI import MidiOutMenuUI


TOOLTIP = "MidiOutMenuUI"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiOutMenuUI' name='MidiOutMenuUI'>
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
    MidiOutMenuUI, module="MidiOutMenuUI", tool_tip=TOOLTIP, xml=DOM_XML
)
