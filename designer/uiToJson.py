from SmartFramework.files import dragAndDrop, read
import xmltodict
import xmljson
import json
from xml.etree.ElementTree import Element, tostring, fromstring


def callback(path):
    print(path)
    xml = read(path)
    # xml_dict = xmltodict.parse(xml)
    print(ET.parse(xml))
    # xml_dict = ET.parse(
    ##xmljson
    dumped_json = json.dumps(xml_dict, indent="\t")
    print(dumped_json)


# callback("D:/Projets/Python/SmartFramework/designer/VideoPlayerUI.ui")
# dragAndDrop(callback = callback,extension = "ui")


xml = read("D:/Projets/Python/SmartFramework/designer/VideoPlayerUI.ui")

# print(json.dumps(xmljson.GData.data(fromstring(xml)),indent='\t'))
print(json.dumps(xmltodict.parse(xml, disable_entities=False), indent="\t"))
# print( ET.parse("D:/Projets/Python/SmartFramework/designer/VideoPlayerUI.ui"))
