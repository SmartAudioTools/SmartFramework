import sys
from SmartFramework.files import dragAndDrop, readLines, write


def callback(path):
    print(path)
    lines = readLines(path)
    new_lines = []
    for line in lines:
        sharp_index = line.find("#")
        if sharp_index != -1 and len(line) > 88:
            line_lstrip = line.lstrip(" ")
            if line_lstrip[0] not in "#)]}":
                indent = " " * (len(line) - len(line_lstrip))
                if (
                    line_lstrip.startswith("if ")
                    or line_lstrip.startswith("elif ")
                    or line_lstrip.startswith("else")
                    or line_lstrip.startswith("def ")
                    or line_lstrip.startswith("class ")
                ):
                    new_lines.append(line[:sharp_index])
                    new_lines.append(indent + "    " + line[sharp_index:])
                else:
                    new_lines.append(indent + line[sharp_index:] + ":")
                    new_lines.append(line[:sharp_index])
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    write(path, new_lines)


sys.argv = ["", "D:/Projets/Python/SmartFramework"]
dragAndDrop(callback=callback, extension=["py", "pyw"], recursive=True)
