from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.video.WebcamMenuUI import WebcamMenuUI


TOOLTIP = "WebcamMenuUI"
DOM_XML = """
<ui language='c++'>
    <widget class='WebcamMenuUI' name='WebcamMenuUI'>
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
    WebcamMenuUI, module="WebcamMenuUI", tool_tip=TOOLTIP, xml=DOM_XML
)
