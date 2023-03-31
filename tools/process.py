# -*- coding: utf-8 -*-
"""
Je me suis basé sur psutil.Process, mais il manque affichage de la description du processus pour ProcessusViewerUI.py 

"""

import os
import psutil
import numpy
from SmartFramework.tools.memory import GlobalMemoryStatusEx, bytes2human
from SmartFramework.files import description
import sys
import subprocess
from ctypes import byref, c_ulong  # , create_string_buffer, ,

try:
    from ctypes import windll

    user32 = windll.user32
    kernel32 = windll.kernel32
    # psapi = windll.psapi

    processPriorityStrToConst = {
        "Idle": psutil.IDLE_PRIORITY_CLASS,  # psutil peut etre remplacer par win32process
        "Below": psutil.BELOW_NORMAL_PRIORITY_CLASS,
        "Normal": psutil.NORMAL_PRIORITY_CLASS,
        "Above Normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
        "High": psutil.HIGH_PRIORITY_CLASS,
        "Real Time": psutil.REALTIME_PRIORITY_CLASS,
    }

    processPriorityConstToStr = {
        value: key for key, value in processPriorityStrToConst.items()
    }

except:
    pass


def getProcessNames():
    return [p.name() for p in psutil.process_iter()]


def find_procs_by_name(name):

    if isinstance(name, str):
        names = [name]
    elif isinstance(name, (list, tuple)):
        names = name
    else:
        raise Exception("find_procs_by_name(name) : name must be a string or a list")
    "Return a list of processes matching 'name'."
    # https://psutil.readthedocs.io/en/latest/#find-process-by-name
    ls = []
    for p in psutil.process_iter(attrs=["name", "exe"]):
        if (p.info["name"] in names) or (
            p.info["exe"] and os.path.basename(p.info["exe"]) in names
        ):
            ls.append(p)
    return ls


def kill(name):
    for process in find_procs_by_name(name):
        process.kill()


def suspend(name):
    processList = find_procs_by_name(name)
    for process in processList:
        process.suspend()
    return processList


def process_iter(attrs=None, ad_value=None):
    for p in psutil.process_iter(attrs=attrs, ad_value=ad_value):
        yield Process(p.pid)


def foregroundProcess():
    hwnd = user32.GetForegroundWindow()
    kernel32.CloseHandle(hwnd)  # close handles
    pid_c = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid_c))
    pid = pid_c.value
    return Process(pid)


class Process(psutil.Process):  # classe pour un seul processus
    """
    SmartFramework : inherit from psutil.Process
    adding all methodes from psutil.Popen and few more methodes

    from psutil.Popen : -----------------
    A more convenient interface to stdlib subprocess.Popen class.
    It starts a sub process and deals with it exactly as when using
    subprocess.Popen class but in addition also provides all the
    properties and methods of psutil.Process class as a unified
    interface:

      >>> import psutil
      >>> from subprocess import PIPE
      >>> p = psutil.Popen(["python", "-c", "print 'hi'"], stdout=PIPE)
      >>> p.name()
      'python'
      >>> p.uids()
      user(real=1000, effective=1000, saved=1000)
      >>> p.username()
      'giampaolo'
      >>> p.communicate()
      ('hi\n', None)
      >>> p.terminate()
      >>> p.wait(timeout=2)
      0
      >>>

    For method names common to both classes such as kill(), terminate()
    and wait(), psutil.Process implementation takes precedence.

    Unlike subprocess.Popen this class pre-emptively checks whether PID
    has been reused on send_signal(), terminate() and kill() so that
    you don't accidentally terminate another process, fixing
    http://bugs.python.org/issue6973.

    For a complete documentation refer to:
    http://docs.python.org/library/subprocess.html
    """

    def __init__(
        self,
        name_or_pid_or_args=None,
        name=None,
        pid=None,
        args=None,
        priority=None,
        cpuAffinity=None,
        wait=False,
        minimized=False,
        hidden=False,
        **kwargs
    ):
        self.__subproc = None
        if name_or_pid_or_args is not None:
            if isinstance(name_or_pid_or_args, str):
                name = name_or_pid_or_args
            elif isinstance(name_or_pid_or_args, int):
                pid = name_or_pid_or_args
            elif isinstance(name_or_pid_or_args, (list, tuple)):
                args = name_or_pid_or_args
            else:
                raise Exception()
        if args:
            # Explicitly avoid to raise NoSuchProcess in case the process
            # spawned by subprocess.Popen terminates too quickly, see:
            # https://github.com/giampaolo/psutil/issues/193

            startupinfo = subprocess.STARTUPINFO()
            if minimized or hidden:

                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                if minimized:
                    startupinfo.wShowWindow = 6  # Run Minimized:
                if hidden:
                    startupinfo.wShowWindow = 0  # Run Hidden
            self.__subproc = subprocess.Popen(args, startupinfo=startupinfo, **kwargs)
            pid = self.__subproc.pid
            self._init(pid, _ignore_nsp=True)
        elif name is not None:
            # https://psutil.readthedocs.io/en/latest/#find-process-by-name
            for p in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
                if (
                    name == p.info["name"]
                    or p.info["exe"]
                    and os.path.basename(p.info["exe"]) == name
                    or p.info["cmdline"]
                    and p.info["cmdline"][0] == name
                ):
                    pid = p.pid()
                    self._init(pid=pid)
                    break
            else:
                # name not found
                raise Exception()
        elif pid:
            self._init(pid=pid)
        elif name_or_pid_or_args is None:
            pid = os.getpid()
            self._init(pid=pid)
        else:
            raise Exception()

        self.currentProcess = currentProcess = os.getpid() == pid
        if currentProcess:
            # self.maxMemory = GlobalMemoryStatusEx().ullTotalVirtual
            self.architecture = sys.maxsize.bit_length() + 1
        else:
            try:
                if (
                    self.environ()["PROCESSOR_ARCHITECTURE"] == "x86"
                ):  # False : # plante de temp en temps quand lance Benchmark C++ .
                    self.architecture = 32
                    self.maxMemory = 1500 * (1024**2)
                else:
                    self.architecture = 64
                    self.maxMemory = None
            except:
                pass
        if priority is not None:
            self.setPriority(priority)
        if cpuAffinity is not None:
            self.setCpuAffinity(cpuAffinity)
        if wait:
            self.wait()
        #

    # Infos ----------------------

    # oneshot() Utility context manager which considerably speeds up the retrieval of multiple process information at the same time. Internally different process info (e.g. name(), ppid(), uids(), create_time(), …) may be fetched by using the same routine, but only one value is returned and the others are discarded. When using this context manager the internal routine is executed once (in the example below on name()) the value of interest is returned and the others are cached. The subsequent calls sharing the same internal routine will return the cached value
    # pid :     The process PID. This is the only (read-only) attribute of the class.
    # ppid()    The process parent PID. On Windows the return value is cached after first call.
    # name()    The process name.
    # exe()     The process executable as an absolute path. On some systems this may also be an empty string.
    # cmdline() The command line this process has been called with as a list of strings. The return value is not cached because the cmdline of a process may change.
    # as_dict(..) Utility method retrieving multiple process information as a dictionary.
    # parent()  Utility method which returns the parent process as a Process object preemptively checking whether PID has been reused. If no parent PID is known return None
    # children(recursive=False) Return the children of this process as a list of Process instances. If recursive is True return all the parent descendants.
    # cwd()    The process current working directory as an absolute path.
    # environ() The environment variables of the process as a dict. Note: this might not reflect changes made after the process started.
    # create_time() The process creation time as a floating point number expressed in seconds since the epoch, in UTC. The return value is cached after first call.
    # status() The current process status as a string. The returned string is one of the psutil.STATUS_* constants.
    # username() The name of the user that owns the process. On UNIX this is calculated by using real process uid.
    # io_counters() return process I/O statistics as a named tuple.
    # num_ctx_switches()  The number voluntary and involuntary context switches performed by this process (cumulative).

    # Windows ----------
    # num_handles   The number of handles currently used by this process (non cumulative).
    # Linux -----------------
    # uids() The real, effective and saved user ids of this process as a named tuple. This is the same as os.getresuid() but can be used for any process PID.
    # gids()The real, effective and saved group ids of this process as a named tuple. This is the same as os.getresgid() but can be used for any process PID.
    # terminal()    The terminal associated with this process, if any, else None. This is similar to “tty” command but can be used for any process PID
    # rlimit(resource, limits=None)     Get or set process resource limits (see man prlimit). resource is one of the psutil.RLIMIT_* constants. limits is a (soft, hard) tuple. This is the same as resource.getrlimit() and resource.setrlimit() but can be used for any process PID, not only os.getpid(). For get, return value is a (soft, hard) tuple. Each value may be either and integer or psutil.RLIMIT_*

    def description(self):
        try:
            return description(self.exe())
        except:
            return None

    # Supend / Resume / Kill ------
    # suspend()
    # resume()
    # terminate()  On Windows this is an alias for kill().
    # kill() Kill the current process On Windows this is done by using TerminateProcess.
    # is_running() Return whether the current process is running in the current process list.
    # send_signal() Send a signal to process (see signal module constants) preemptively checking whether PID has been reused. On UNIX this is the same as os.kill(pid, sig). On Windows only SIGTERM, CTRL_C_EVENT and CTRL_BREAK_EVENT signals are supported and SIGTERM is treated as an alias for kill()

    # Memory ------------------
    # memory_info() Return a named tuple with variable fields depending on the platform representing memory information about the process.
    # memory_full_info()  This method returns the same information as memory_info(), plus "uss" aka “Unique Set Size”, this is the memory which is unique to a process and which would be freed if the process was terminated right now. The additional metrics provide a better representation of “effective” process memory consumption (in case of USS) as explained in detail in this blog post. It does so by passing through the whole process address. As such it usually requires higher user privileges than memory_info() and is considerably slower
    # memory_percent(memtype="rss")    Compare process memory to total physical system memory and calculate process memory utilization as a percentage. memtype argument is a string that dictates what type of process memory you want to compare against.
    # memory_maps(grouped=True)  Return process’s mapped memory regions as a list of named tuples whose fields are variable depending on the platform.

    def getUsedMemory(self):
        return self.memory_info().rss

    def getAvailableMemory(self):
        if self.architecture == 32:
            if self.currentProcess and False:
                return (
                    GlobalMemoryStatusEx().ullAvailVirtual
                )  # pb ne redescent pas quand je l'utiliser avec camera par exemple alors que marche sur simple script (cf le __main__ plus bas) ... https://stackoverflow.com/questions/26065524/memorystatusex-and-globalmemorystatusex
            else:
                totalFreeMemory = psutil.virtual_memory().available
                return min(totalFreeMemory, self.maxMemory - self.memory_info().rss)
        else:
            # ATTENTION NE SERA PAS VALIDE POUR PROCESSUS 32 bit
            return psutil.virtual_memory().available

    # In / Out -----------------------
    def getOpenPaths(self):
        """Warning : on Windows this method is not reliable due to some limitations of the underlying Windows API which may hang when retrieving certain file handles. In order to work around that psutil spawns a thread for each handle and kills it if it’s not responding after 100ms. That implies that this method on Windows is not guaranteed to enumerate all regular file handles (see issue 597). Also, it will only list files living in the C:\ drive (see issue 1020)."""
        return [namedTuple.path for namedTuple in self.open_files()]

    # CPU --------------
    # num_threads()     The number of threads currently used by this process (non cumulative).
    # threads() Return threads opened by process as a list of named tuples including thread id and thread CPU times (user/system)
    # cpu_times Return a (user, system, children_user, children_system) named tuple representing the accumulated process time, in seconds (see explanation). On Windows and macOS only user and system are filled, the others are set to 0. This is similar to os.times() but can be used for any process PID.
    # cpu_percent Return a float representing the process CPU utilization as a percentage which can also be > 100.0 in case of a process running multiple threads on different CPUs.
    # cpu_num() Return what CPU this process is currently running on.

    def setCpuAffinity(self, cpus):
        if not numpy.iterable(cpus):
            cpus = [cpus]
        self.cpu_affinity(cpus)

    def getCpuAffinity(self):
        return self.cpu_affinity()

    def setPriority(self, priority):
        self.nice(processPriorityStrToConst[priority])

    def getPriority(self):
        return processPriorityConstToStr[self.nice()]

    # Methodes récuperée de psytil.Popen --------------------------

    def __dir__(self):
        """recupéré de psytil.Popen.__dir__"""
        return sorted(set(dir(Process) + dir(subprocess.Popen)))

    def __enter__(self):
        """recupéré de psytil.Popen.__enter__"""
        if hasattr(self, "__subproc") and hasattr(self.__subproc, "__enter__"):
            self.__subproc.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        """recupéré de psytil.Popen.__exit__"""
        if hasattr(self, "__subproc") and hasattr(self.__subproc, "__exit__"):
            return self.__subproc.__exit__(*args, **kwargs)
        else:
            if self.stdout:
                self.stdout.close()
            if self.stderr:
                self.stderr.close()
            try:
                # Flushing a BufferedWriter may raise an error.
                if self.stdin:
                    self.stdin.close()
            finally:
                # Wait for the process to terminate, to avoid zombies.
                self.wait()

    def __getattribute__(self, name):
        """recupéré de psytil.Popen.__getattribute__"""
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            try:
                return object.__getattribute__(self.__subproc, name)
            except AttributeError:
                raise AttributeError(
                    "%s instance has no attribute '%s'"
                    % (self.__class__.__name__, name)
                )

    def wait(self, timeout=None):
        """recupéré de psytil.Popen.wait"""
        if self.__subproc.returncode is not None:
            return self.__subproc.returncode
        ret = super(Process, self).wait(timeout)
        self.__subproc.returncode = ret
        return ret


if __name__ == "__main__":

    from collections import deque
    import gc

    # ----------------
    process = Process()
    print(process)
    print("inital process max %s" % bytes2human(process.maxMemory))
    print(
        "inital process used + available %s"
        % bytes2human(process.getUsedMemory() + process.getAvailableMemory())
    )
    print("inital process used %s" % bytes2human(process.getUsedMemory()))
    print("inital process available %s" % bytes2human(process.getAvailableMemory()))

    all = deque()
    try:
        while True:
            all.append(numpy.ones(1024 * 1024, numpy.int8))
    except:
        pass
    all.popleft()
    new = numpy.ones(1024 * 1024, numpy.int8)
    print("full process used %s" % bytes2human(process.getUsedMemory()))
    print("full process available %s" % bytes2human(process.getAvailableMemory()))
    print("full process max %s" % bytes2human(process.maxMemory))
    print(
        "full process used + available %s"
        % bytes2human(process.getUsedMemory() + process.getAvailableMemory())
    )

    del all
    gc.collect()
    print("after cleaning process used %s" % bytes2human(process.getUsedMemory()))
    print(
        "after cleaning process available %s"
        % bytes2human(process.getAvailableMemory())
    )
    print("after process max %s" % bytes2human(process.maxMemory))
    print(
        "after process used + available %s"
        % bytes2human(process.getUsedMemory() + process.getAvailableMemory())
    )

    os.system("pause")
