from PyRTF.Elements import Document
from PyRTF.document.section import Section
from PyRTF.Renderer import Renderer
from PyRTF.document.paragraph import Paragraph
from PyRTF.document.character import TEXT


class Rtf:
    def __init__(self, path=None):
        self.doc = Document()
        self.section = Section()
        self.doc.Sections.append(self.section)
        self.path = path

    def setPath(self, path):
        self.path = path

    def append(self, s, colour=None):
        p = Paragraph()
        s2 = s.encode("unicode_escape").decode("ascii").replace("\\x", "\\'")
        if colour is not None:
            p.append(
                TEXT(s2, colour=eval("self.doc.StyleSheet.Colours." + colour.title()))
            )
        else:
            p.append(s)
        self.section.append(p)

    def write(self, path=None):
        if path is None:
            path = self.path
        DR = Renderer()
        DR.Write(self.doc, open(path, "w", encoding="ascii"))


if __name__ == "__main__":
    rtf = Rtf("test4.rtf")
    rtf.append("é€▲")
    rtf.write()
