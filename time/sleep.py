from time import perf_counter


def uSleep(sec):
    start = perf_counter()
    end = start + sec - 5.5e-06
    while end > perf_counter():
        pass
