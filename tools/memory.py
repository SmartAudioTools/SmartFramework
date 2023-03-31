import psutil
from ctypes import sizeof, byref, c_ulonglong, Structure
from ctypes.wintypes import DWORD
import os


try:
    from ctypes import windll
except:
    pass


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return "%.1f%s" % (value, s)
    return "%sB" % n


def pprint_ntuple(nt):
    for name in nt._fields:
        value = getattr(nt, name)
        if name != "percent":
            value = bytes2human(value)
        print("%-10s : %7s" % (name.capitalize(), value))


def getUsedMemory(process=None):
    if process is None:
        process = psutil.Process()
    return process.memory_info().rss


def getAvailableDiskSpace(path):
    freeDiskSpace = psutil.disk_usage(os.path.splitdrive(path)[0]).free
    return freeDiskSpace


def getAvailableMemory(
    process=None, maxMemory=None, architecture=None, currentProcess=None
):
    if process is None:
        process = psutil.Process()
        currentProcess = True
    elif currentProcess is None:
        currentProcess = os.getpid() == process.pid
    if architecture is None:
        if process.environ()["PROCESSOR_ARCHITECTURE"] == "x86":
            architecture = 32
        else:
            architecture = 64
    if architecture == 32:
        if maxMemory is None:
            if currentProcess:
                maxMemory = GlobalMemoryStatusEx().ullTotalVirtual
            else:
                maxMemory = 1500 * (1024**2)
        if currentProcess and False:
            return (
                GlobalMemoryStatusEx().ullAvailVirtual
            )  # pb ne redescent pas quand je l'utiliser avec camera par exemple alors que marche sur simple script (cf le __main__ plus bas) ... https://stackoverflow.com/questions/26065524/memorystatusex-and-globalmemorystatusex
        else:
            totalFreeMemory = psutil.virtual_memory().available
            return min(totalFreeMemory, maxMemory - process.memory_info().rss)
    else:
        # ATTENTION NE SERA PAS VALIDE POUR PROCESSUS 32 bit
        return psutil.virtual_memory().available


class MEMORYSTATUSEX(Structure):
    _fields_ = [
        ("dwLength", DWORD),
        ("dwMemoryLoad", DWORD),
        ("ullTotalPhys", c_ulonglong),
        ("ullAvailPhys", c_ulonglong),
        ("ullTotalPageFile", c_ulonglong),
        ("ullAvailPageFile", c_ulonglong),
        ("ullTotalVirtual", c_ulonglong),
        ("ullAvailVirtual", c_ulonglong),
        ("ullExtendedVirtual", c_ulonglong),
    ]


def GlobalMemoryStatusEx():
    x = MEMORYSTATUSEX()
    x.dwLength = sizeof(x)
    windll.kernel32.GlobalMemoryStatusEx(byref(x))
    return x


if __name__ == "__main__":
    p = psutil.Process()
    print("MEMORY\n------")
    pprint_ntuple(psutil.virtual_memory())
    print("\nSWAP\n----")
    pprint_ntuple(psutil.swap_memory())
    print("\nmemory_info\n----")
    pprint_ntuple(p.memory_info())
    print("\nmemory_full_info\n----")
    pprint_ntuple(p.memory_full_info())
