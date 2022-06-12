# ==============================================================================
#  Copyright (C) 2021-2022. tetgs authors
#
#  This file is a part of tetgs, which is licensed under MIT,
#  a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
#  NAME: proc_monitor.py -- Process Monitor
#
#  VERSION HISTORY:
#  2021-08-26 0.1  : Migrated from LinuxMiniPrograms.
#
# ==============================================================================
"""
pid_monitor -- A General-Purposed Python-Implemented Process Monitor

This is a monitor implemented in UNIX ProcFS and :py:mod:`psutils`.
This module should work on any GNU/Linux distributions that have above modules.

To use this module as an **executable**, see :py:mod:`__main__`.

To use this module in your own project, see :py:mod:`main_func`.
"""

from __future__ import annotations

__version__ = "0.3"

import logging
import time

import psutil

logging.basicConfig(
    level=logging.DEBUG,
    filename="tracer.log",
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s: %(message)s'
)

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


def to_human_readable(num: int, base: int = 1024) -> str:
    """
    Make an integer to 1000- or 1024-based human-readable form.
    """
    if base == 1024:
        dc_list = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
    elif base == 1000:
        dc_list = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    else:
        raise ValueError("base should be 1000 or 1024")
    step = 0
    dc = dc_list[step]
    while num > base and step < len(dc_list) - 1:
        step = step + 1
        num /= base
        dc = dc_list[step]
    num = round(num, 2)
    return str(num) + dc
