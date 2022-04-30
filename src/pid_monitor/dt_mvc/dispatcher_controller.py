import gc
import signal
import time
from typing import Dict, Union

from pid_monitor import DEFAULT_SYSTEM_INDICATOR_PID
from pid_monitor.dt_mvc.base_dispatcher_class import BaseTracerDispatcherThread

_DISPATCHERS: Dict[int, BaseTracerDispatcherThread] = {}
"""Dict[pid, Dispatcher] for all active dispatchers"""


def terminate_all_dispatchers(_signal: Union[signal.signal, int] = signal.SIGTERM, *_args):
    """
    Send signal to all dispatchers.
    """
    for val in _DISPATCHERS.values():
        try:
            val.should_exit = True
        except AttributeError:
            del val
    time.sleep(2)
    _DISPATCHERS.clear()
    gc.collect()


def get_current_active_pids():
    return _DISPATCHERS.keys()


def register_dispatcher(pid: int, dispatcher: BaseTracerDispatcherThread):
    _DISPATCHERS[pid] = dispatcher


def collect_all_process_info() -> Dict[int, Dict[str, str]]:
    retd = {}
    for d_pid, d_val in _DISPATCHERS.items():
        if d_pid != DEFAULT_SYSTEM_INDICATOR_PID:
            retd[d_pid] = d_val.collect_information()
    return retd


def collect_system_info() -> Dict[str, str]:
    return _DISPATCHERS[DEFAULT_SYSTEM_INDICATOR_PID].collect_information()


def remove_dispatcher(pid: int):
    try:
        _DISPATCHERS.pop(pid)
    except KeyError:
        pass
