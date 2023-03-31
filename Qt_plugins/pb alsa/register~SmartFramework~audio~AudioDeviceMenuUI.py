from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.audio.AudioDeviceMenuUI import AudioDeviceMenuUI


TOOLTIP = "AudioDeviceMenuUI"
DOM_XML = """
<ui language='c++'>
    <widget class='AudioDeviceMenuUI' name='AudioDeviceMenuUI'>
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
    AudioDeviceMenuUI, module="AudioDeviceMenuUI", tool_tip=TOOLTIP, xml=DOM_XML
)
