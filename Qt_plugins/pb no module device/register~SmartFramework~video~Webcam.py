from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from SmartFramework.video.Webcam import Webcam


TOOLTIP = "Webcam"
DOM_XML = """
<ui language='c++'>
    <widget class='Webcam' name='Webcam'>
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
    Webcam, module="Webcam", tool_tip=TOOLTIP, xml=DOM_XML
)
