import subprocess
from logging import getLogger
from time import sleep

from prettytable import PrettyTable

from pid_monitor._private.dt_mvc.base_dispatcher_class import DispatcherController

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


def _print_frontend_system_tracer(dispatcher_controller: DispatcherController):
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


def _print_frontend_process_tracer(
        process_table: PrettyTable,
        dispatcher_controller: DispatcherController
):
    all_info = dispatcher_controller.collect_all_process_info()
    for pid_val in all_info.values():
        row = [pid_val[name] for name in _PROCESS_TABLE_COL_NAMES]
        process_table.add_row(row)
    print(process_table)
    process_table.clear_rows()


def show_frontend(
        frontend_refresh_interval: float,
        dispatcher_controller: DispatcherController
):
    """Show the frontend."""
    process_table = PrettyTable(_PROCESS_TABLE_COL_NAMES)
    while len(dispatcher_controller.get_current_active_pids()) > 1:
        subprocess.call('clear')
        _print_frontend_system_tracer(dispatcher_controller=dispatcher_controller)
        _print_frontend_process_tracer(
            process_table=process_table,
            dispatcher_controller=dispatcher_controller
        )
        sleep(frontend_refresh_interval)
    _LOGGER_HANDLER.info("Toplevel PID finished")
