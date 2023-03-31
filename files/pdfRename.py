import os
import sys

try:
    from SmartFramework.files import dragAndDrop
    from pdfrenamer import rename

    def pdfrename(path):
        try:
            rename(path, format="[{YYYY}] {T}")
        except:
            print(sys.exc_info()[1])

    dragAndDrop(
        callback=pdfrename,
        group=False,
        recursive=True,
        extension=["pdf"],
    )
    os.system("pause")
except:
    import sys

    print(sys.exc_info()[1])
os.system("pause")
