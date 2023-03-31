import sys
from SmartFramework.files import dragAndDrop, readLines, write


def callback(path):
    print(path)
    modifie = False
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
                modifie = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    new_lines2 = []
    for line in new_lines:
        print_index = sharp_index = line.find("print ")
        if print_index != -1 and (print_index == 0 or line[print_index - 1] == " "):
            start_quotation = line[print_index + 6]
            if start_quotation not in ["'", '"']:
                start_quotation = " "
            modifie = True
            # end = line.find(start_quotation,print_index+7)+1
            # if end ==0  :
            end = len(line)
            line = (
                line[: print_index + 5]
                + "("
                + line[print_index + 6 : end]
                + ")"
                + line[end:]
            )
        new_lines2.append(line)
    if modifie:
        write(path, new_lines2)


sys.argv = ["", "D:/Projets/Python/SmartFramework"]
dragAndDrop(callback=callback, extension=["py", "pyw"], recursive=True)
