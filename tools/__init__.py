# from objects import *
# from files import *
# from dictionnaires import *


def inclusiveRange(start, stop, step=1):
    if stop < start:
        step = -abs(step)
    else:
        step = abs(step)
    return range(start, (stop + 1) if step >= 0 else (stop - 1), step)
