from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.video.WebcamUI import WebcamUI


TOOLTIP = "WebcamUI"
DOM_XML = """
<ui language='c++'>
    <widget class='WebcamUI' name='WebcamUI'>
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
    WebcamUI, module="WebcamUI", tool_tip=TOOLTIP, xml=DOM_XML
)
