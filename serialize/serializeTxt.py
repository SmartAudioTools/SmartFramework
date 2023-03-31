from io import IOBase
from SmartFramework.files import write, readLines
from SmartFramework.string import addNewlines


def load(f):
    if isinstance(f, str):
        return readLines(f, iterator=False)
    elif isinstance(f, IOBase):
        return f.read().splitlines()
    else:
        raise Exception("l'arg de picklePyton.load() doit être un file ou str")


def dump(lines, f):
    # tente ecriture
    if isinstance(f, str):
        write(f, lines)  # les \n sont remplacés par des \r\n !?
    elif isinstance(f, IOBase):
        f.writelines(addNewlines(lines))
    else:
        raise Exception(
            "fichier incorrect (file ou str) pour sauver l'objet" + str(lines)
        )
