import gc
import importlib
import signal
import threading
import time
from typing import Union, Iterator, Tuple

POSSIBLE_TRACER_PATHS = (
    "pid_monitor.std_tracer",
    "pid_monitor.additional_tracers"
)

_REG_MUTEX = threading.Lock()
"""Mutex for writing registries"""

_DISPATCHER_MUTEX = threading.Lock()
"""Mutex for creating dispatchers for new process/thread"""


def get_tracer(name: str):
    """
    Return a known tracer.
    """
    for possible_path in POSSIBLE_TRACER_PATHS:
        try:
            mod = importlib.import_module(possible_path)
            return getattr(mod, name)
        except ModuleNotFoundError:
            continue
    raise ModuleNotFoundError


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


_DISPATCHERS = {}
"""Dict[pid, Dispatcher] for all active dispatchers"""


def list_tracer() -> Iterator[Tuple[str, str]]:
    """
    List all available tracer
    """
    for possible_path in POSSIBLE_TRACER_PATHS:
        try:
            mod = importlib.import_module(possible_path)
            for k, v in mod.__dict__.items():
                if k.__contains__("Tracer") and not k.startswith("Base"):
                    try:
                        yield k, v.__doc__.strip()
                    except AttributeError:
                        yield k, "No docs available"
        except ModuleNotFoundError:
            continue
