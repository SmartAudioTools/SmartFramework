import win32con, win32process
import psutil


"""
CREER INTERFACE POUR: 
psutil.Process().num_threads()
psutil.Process().threads()
win32process.SetThreadPriority
win32process.GetThreadPriority
win32process.GetThreadTimes     # Returns a thread's time statistics 
# Used to specify a preferred processor for a thread. The system schedules threads on their preferred processors whenever possible. :
win32process.SetThreadIdealProcessor 
# Sets a processor affinity mask for a specified thread. :
win32process.SetThreadAffinityMask 
"""

threadPriorityStrToConst = {
    "Idle": win32con.THREAD_PRIORITY_IDLE,
    "Lowest": win32con.THREAD_PRIORITY_LOWEST,
    "Below Normal": win32con.THREAD_PRIORITY_BELOW_NORMAL,
    "Normal": win32con.THREAD_PRIORITY_NORMAL,
    "Above Normal": win32con.THREAD_PRIORITY_ABOVE_NORMAL,
    "Highest": win32con.THREAD_PRIORITY_HIGHEST,
    "Time Critical": win32con.THREAD_PRIORITY_TIME_CRITICAL,
}
