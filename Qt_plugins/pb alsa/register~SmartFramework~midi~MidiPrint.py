from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.midi.MidiPrint import MidiPrint


TOOLTIP = "MidiPrint"
DOM_XML = """
<ui language='c++'>
    <widget class='MidiPrint' name='MidiPrint'>
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
    MidiPrint, module="MidiPrint", tool_tip=TOOLTIP, xml=DOM_XML
)
