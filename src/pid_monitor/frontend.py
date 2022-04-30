import subprocess
from logging import getLogger
from time import sleep

from prettytable import PrettyTable

from pid_monitor import DEFAULT_REFRESH_INTERVAL
from pid_monitor.dt_mvc import dispatcher_controller

_LOGGER_HANDLER = getLogger(__name__)

_PROCESS_TABLE_COL_NAMES = (
    'PID',
    'PPID',
    'NAME',
    'STAT',
    'CPU%',
    'CPU_TIME',
    'RESIDENT_MEM',
    'NUM_THREADS',
    'NUM_CHILD_PROCESS'
)


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
    all_info = dispatcher_controller.collect_system_info()
    print("".join((
        "CPU%: ", all_info['CPU%'], "; ",
        "VIRTUALMEM: ",
        "AVAIL: ", all_info['VM_AVAIL'], "/", all_info['VM_TOTAL'], "=(", all_info['VM_PERCENT'], "), ",
        "BUFFERED: ", all_info['BUFFERED'], ", ", "SHARED: ", all_info['SHARED'], "; ",
        "SWAP: ",
        "AVAIL: ", all_info['SWAP_AVAIL'], "/", all_info['SWAP_TOTAL'], "=(", all_info['SWAP_PERCENT'], ") "
    ))
    )


def _print_frontend_process_tracer(process_table: PrettyTable):
    all_info = dispatcher_controller.collect_all_process_info()
    for pid_val in all_info.values():
        row = [pid_val[name] for name in _PROCESS_TABLE_COL_NAMES]
        process_table.add_row(row)
    print(process_table)
    process_table.clear_rows()


def show_frontend(
        interval: float = DEFAULT_REFRESH_INTERVAL
):
    """Show the frontend."""
    process_table = PrettyTable(_PROCESS_TABLE_COL_NAMES)
    while len(dispatcher_controller.get_current_active_pids()) > 1:
        subprocess.call('clear')
        _print_frontend_system_tracer()
        _print_frontend_process_tracer(process_table)
        sleep(interval * 100)
    _LOGGER_HANDLER.info("Toplevel PID finished")
