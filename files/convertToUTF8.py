from SmartFramework.files import dragAndDrop, searchExt, readLines, writeLines


def convertToUtf8(path):
    lines = readLines(path)
    writeLines(path, lines, encoding="utf-8")


dragAndDrop(callback=convertToUtf8, extension=["py", "pyw"], recursive=True)
