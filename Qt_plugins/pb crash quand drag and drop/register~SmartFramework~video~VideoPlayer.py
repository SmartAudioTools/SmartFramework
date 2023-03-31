from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.video.VideoPlayer import VideoPlayer


TOOLTIP = "VideoPlayer"
DOM_XML = """
<ui language='c++'>
    <widget class='VideoPlayer' name='VideoPlayer'>
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
    VideoPlayer, module="VideoPlayer", tool_tip=TOOLTIP, xml=DOM_XML
)
