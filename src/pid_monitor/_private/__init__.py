from __future__ import annotations

import time

import psutil

PSUTIL_NOTFOUND_ERRORS = (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied, psutil.Error)
"""Some common psutil errors."""

DEFAULT_REFRESH_INTERVAL = 0.01
DEFAULT_SYSTEM_INDICATOR_PID = -1
DEFAULT_PROCESS_LEVEL_TRACERS = [
    "ProcessIOTracerThread",
    "ProcessFDTracerThread",
    "ProcessMEMTracerThread",
    "ProcessChildTracerThread",
    "ProcessCPUTracerThread",
    "ProcessSTATTracerThread",
    "ProcessSyscallTracerThread"
]
DEFAULT_SYSTEM_LEVEL_TRACERS = [
    "SystemMEMTracerThread",
    "SystemCPUTracerThread",
    "SystemSWAPTracerThread"
]


def get_total_cpu_time(_p: psutil.Process) -> float:
    """
    Get total CPU time for a process.
    Should return time spent in system mode (aka. kernel mode) and user mode.
    """
    try:
        cpu_time_tuple = _p.cpu_times()
        return cpu_time_tuple.system + cpu_time_tuple.user
    except PSUTIL_NOTFOUND_ERRORS:
        return -1


def get_timestamp() -> str:
    """
    Get timestamp in an accuracy of 0.01 seconds.
    """
    time_in_ms = time.time() * 100
    return time.strftime(f'%Y-%m-%d %H:%M:%S.{int(time_in_ms % 100)}', time.localtime(time_in_ms / 100.0))


def to_human_readable(
        num: int,
        base: int = 1024,
        suffix: str = "B"
) -> str:
    """
    Make an integer to 1000- or 1024-based human-readable form.
    """
    if base == 1024:
        dc_list = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']
    elif base == 1000:
        dc_list = ['', 'K', 'M', 'G', 'T', 'P', 'E']
    else:
        raise ValueError("base should be 1000 or 1024")
    step = 0
    dc = dc_list[step]
    while num > base and step < len(dc_list) - 1:
        step = step + 1
        num /= base
        dc = dc_list[step]
    num = round(num, 2)
    return str(num) + dc + suffix
