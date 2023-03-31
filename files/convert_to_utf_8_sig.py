import os

try:
    from SmartFramework.files import dragAndDrop, read, write

    def convert_to_utf_8_sig(path):
        string, encoding = read(path, return_encoding=True)
        print(path, encoding)
        if encoding != "utf_8_sig":
            print(f"convert {encoding} -> utf_8_sig : {path}")
            write(path, string)

    dragAndDrop(
        callback=convert_to_utf_8_sig,
        group=False,
        recursive=True,
        extension=["py", "pyw"],
    )
    os.system("pause")
except:
    import sys

    print(sys.exc_info()[1])
os.system("pause")
