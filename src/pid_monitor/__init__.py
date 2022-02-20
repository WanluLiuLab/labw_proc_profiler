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

__version__ = 0.2

import logging
import time

import psutil

_ALL_PIDS = set()
logging.basicConfig(
    level=logging.DEBUG,
    filename="tracer.log",
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s: %(message)s'
)

PSUTIL_NOTFOUND_ERRORS = (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied, psutil.Error)
"""Some common psutil errors."""

DEFAULT_REFRESH_INTERVAL = 0.01


def get_total_cpu_time(_p: psutil.Process) -> float:
    """
    Get total CPU time for a process.
    Should return time spent in system mode (aka. kernel mode) and user mode.
    """
    cpu_time_tuple = _p.cpu_times()
    return cpu_time_tuple.system + cpu_time_tuple.user


def get_timestamp() -> str:
    """
    Get timestamp in an accuracy of 0.01 seconds.
    """
    time_in_ms = time.time() * 1000
    return time.strftime(f'%Y-%m-%d %H:%M:%S.{int(time_in_ms % 100)}', time.localtime(time_in_ms / 100.0))
