from SmartFramework.files import dragAndDrop, read, write, addToName
from math import ceil, log10


def split_in_chunks(path, nb_lines=100):
    string, encoding = read(path, encoding=["utf_8", "cp1252"], return_encoding=True)
    lines = string.splitlines()
    total_nb_lines = len(lines)
    np_files = ceil(total_nb_lines / nb_lines)
    nb_digits = int(log10(np_files)) + 1
    format_str = "_part_{:0>%d}" % nb_digits
    for i in range(np_files):
        new_lines = lines[i * nb_lines : (i + 1) * nb_lines]
        new_path = addToName(path, format_str.format(i + 1))
        # print(new_path ,encoding)
        write(new_path, new_lines, encoding=encoding)


# import sys
# sys.argv = ["","D:/Projets/Python/SmartRobots/LISTES/FRIENDS/amis que de jeanne.forclimat.7.txt"]
dragAndDrop(
    callback=split_in_chunks,
)
