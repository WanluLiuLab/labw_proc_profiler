import copy
import subprocess
import threading
from time import sleep

import psutil
from prettytable import PrettyTable

from pid_monitor import get_total_cpu_time, _PSUTIL_NOTFOUND_ERRORS

FRONTEND_ALL_PIDS = set()
"""A set of all process/thread ids that have been traced"""

_PROCESS_TABLE = PrettyTable((
    'PID',
    'PPID',
    'NAME',
    'STAT',
    'CPU%',
    'CPU_TIME',
    'RESIDENT_MEM',
    'NUM_THREADS',
    'NUM_CHILD_PROCESS'
))
"""The process table show at the frontend."""


def _to_human_readable(num: int, base: int = 1024) -> str:
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


def _print_frontend_system_tracer():
    """
    Print frontend system tracer information.
    """
    print(f"CPU%: {psutil.cpu_percent(0.1)}")
    x = psutil.virtual_memory()
    print(
        "VIRTUALMEM: " +
        f"AVAIL: {_to_human_readable(x.available)}/{_to_human_readable(x.total)}" +
        f"={round(x.available / x.total * 100, 2)}%" +
        f"BUFFER: {_to_human_readable(x.buffers)}" +
        f" SHARED {_to_human_readable(x.shared)}")
    x = psutil.swap_memory()
    print(
        f"SWAP: " +
        f"AVAIL: {_to_human_readable(x.free)}/{_to_human_readable(x.total)}" +
        f"={100 - x.percent}% " +
        f"I/O: {_to_human_readable(x.sin)}/{_to_human_readable(x.sout)}")


def _print_frontend_process_tracer():
    thread_pool = []
    all_pids_tmp = copy.deepcopy(FRONTEND_ALL_PIDS)
    for pid in all_pids_tmp:
        thread_pool.append(threading.Thread(_add_row_to_frontend_process_table(pid)))
        thread_pool[-1].start()
    for thread in thread_pool:
        thread.join()
    print(_PROCESS_TABLE)
    _PROCESS_TABLE.clear_rows()


def _add_row_to_frontend_process_table(pid: int):
    """Add a row to the process table"""
    try:
        _process = psutil.Process(pid)
        row = (
            _process.pid,
            _process.ppid(),
            _process.name(),
            _process.status(),
            str(_process.cpu_percent(0.1)),
            str(get_total_cpu_time(_process)),
            str(_to_human_readable(_process.memory_info().rss)),
            _process.num_threads(),
            len(_process.children())
        )
    except _PSUTIL_NOTFOUND_ERRORS:
        FRONTEND_ALL_PIDS.remove(pid)
        return
    _PROCESS_TABLE.add_row(row)


def show_frontend(toplevel_trace_pid: int):
    """Show the frontend."""
    FRONTEND_ALL_PIDS.add(toplevel_trace_pid)
    while psutil.pid_exists(toplevel_trace_pid):
        subprocess.call('clear')
        _print_frontend_system_tracer()
        _print_frontend_process_tracer()
        sleep(1.5)
    print("Toplevel PID finished")
