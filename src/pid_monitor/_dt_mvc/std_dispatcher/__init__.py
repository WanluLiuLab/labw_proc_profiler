from __future__ import annotations

import gc
import importlib
import signal
import threading
import time
from abc import abstractmethod
from typing import Dict, List, Union, Set, Type, Iterator, Tuple

import prettytable

from pid_monitor._dt_mvc import DEFAULT_SYSTEM_INDICATOR_PID
from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.frontend_cache.system_frontend_cache import SystemFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig, POSSIBLE_TRACER_PATHS
from pid_monitor._dt_mvc.std_tracer import BaseTracerThread
from pid_monitor._dt_mvc.typing import ThreadWithPMC



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


class BaseTracerDispatcherThread(ThreadWithPMC):
    """
    The base class of all dispatchers.
    """

    _thread_pool: Dict[str, threading.Thread]
    """The tracer Thread, is name -> thread"""
    _dispatcher_controller: DispatcherController

    _frontend_cache: Union[SystemFrontendCache, ProcessFrontendCache]

    def __init__(
            self,
            trace_pid: int,
            pmc: PMConfig,
            dispatcher_controller: DispatcherController
    ):
        super().__init__(trace_pid=trace_pid, pmc=pmc)
        self._thread_pool = {}
        dispatcher_controller.register_dispatcher(self)
        self._dispatcher_controller = dispatcher_controller

    def append_threadpool(self, thread: threading.Thread):
        self._thread_pool[thread.__class__.__name__] = thread

    def start_tracers(
            self,
            tracers_to_load: List[str]
    ):
        """Start loaded tracers. Should be called at the end of :py:func:`init`."""

        for tracer in tracers_to_load:
            try:
                self.log_handler.info(f"trace_pid={self.trace_pid}: Fetch TRACER={tracer}")
                new_thread = get_tracer_class(tracer)(
                    trace_pid=self.trace_pid,
                    pmc=self.pmc,
                    frontend_cache=self._frontend_cache
                )
                self.log_handler.info(f"trace_pid={self.trace_pid}: Fetch TRACER={tracer} SUCCESS")
            except Exception as e:
                self.log_handler.error(
                    f"trace_pid={self.trace_pid}: "
                    f"Fetch TRACER={tracer} {e.__class__.__name__} encountered! "
                    f"DETAILS={e.__repr__()}"
                )
                raise e
            new_thread.start()
            self.log_handler.info(f"trace_pid={self.trace_pid}: Start TRACER={tracer}")
            self.append_threadpool(new_thread)

    @abstractmethod
    def before_ending(self):
        """
        Method to call to perform clean exit, like writing logs.
        """
        pass

    def run(self):
        self.log_handler.info(f"Dispatcher for trace_pid={self.trace_pid} started")
        self.run_body()
        self.log_handler.info(f"Dispatcher for trace_pid={self.trace_pid} stopped")

    def run_body(self):
        """
        The default runner
        """
        while not self.should_exit:
            time.sleep(self.pmc.backend_refresh_interval)

    def __del__(self):
        """
        Force deletion.
        """
        try:
            self.sigterm()
        except AttributeError:
            pass

    def sigterm(self, *args):
        """
        Sigterm handler. By default, it:

        - Call py:func:`before_ending` method.
        - Terminate all threads in ``_thread_pool``
        - Suicide.
        """
        self.log_handler.info(f"Dispatcher for trace_pid={self.trace_pid} SIGTERM")
        self.before_ending()
        self._dispatcher_controller.remove_dispatcher(self.trace_pid)
        for thread in self._thread_pool.values():
            try:
                thread.should_exit = True
            except AttributeError:
                del thread
        time.sleep(2)
        self._thread_pool.clear()
        gc.collect()

    def __repr__(self):
        try:
            return f"Dispatcher for {self.trace_pid}"
        except AttributeError:
            return "Dispatcher under construction"

    def __str__(self):
        return repr(self)


class DispatcherController:
    _dispatchers: Dict[int, BaseTracerDispatcherThread]
    """Dict[pid, Dispatcher] for all active dispatchers"""

    _frontend_caches: Dict[int, Union[ProcessFrontendCache, SystemFrontendCache]]

    all_pids: Set[int]

    _pretty_table: prettytable.PrettyTable

    def __init__(self):
        self._dispatchers = {}
        self.all_pids = set()
        self._frontend_caches = {}
        self._pretty_table = prettytable.PrettyTable(
            _PROCESS_TABLE_COL_NAMES
        )

    def terminate_all_dispatchers(self, _signal: Union[signal.signal, int] = signal.SIGTERM, *_args):
        """
        Send signal to all dispatchers.
        """
        for val in self._dispatchers.values():
            try:
                val.should_exit = True
            except AttributeError:
                del val
        time.sleep(2)
        self._dispatchers.clear()
        gc.collect()

    def get_current_active_pids(self) -> List[int]:
        return list(self._dispatchers.keys())

    def register_dispatcher(self, dispatcher: BaseTracerDispatcherThread) -> None:
        self._dispatchers[dispatcher.trace_pid] = dispatcher
        self.all_pids.add(dispatcher.trace_pid)

    def remove_dispatcher(self, pid: int) -> None:
        try:
            self._dispatchers.pop(pid)
            self._frontend_caches.pop(pid)
        except KeyError:
            pass

    def register_frontend_cache(self, pid: int, frontend_cache: Union[ProcessFrontendCache, SystemFrontendCache]):
        self._frontend_caches[pid] = frontend_cache

    def _get_system_frontend_cache(self) -> str:
        try:
            return str(self._frontend_caches[DEFAULT_SYSTEM_INDICATOR_PID])
        except KeyError:
            return "Preparing..."

    def _get_process_frontend_cache(self) -> str:
        self._pretty_table.clear_rows()
        for pid, cache in self._frontend_caches.items():
            if pid != DEFAULT_SYSTEM_INDICATOR_PID:
                self._pretty_table.add_row(cache.to_prettytable_row())
        return str(self._pretty_table)

    def get_frontend_cache(self) -> str:
        return "\n".join((
            self._get_system_frontend_cache(),
            self._get_process_frontend_cache()
        ))


def get_tracer_class(name: str) -> Type[BaseTracerThread]:
    """
    Return a known tracer.
    """
    for possible_path in POSSIBLE_TRACER_PATHS:
        try:
            mod = importlib.import_module(possible_path)
            return getattr(mod, name)
        except (ModuleNotFoundError, AttributeError):
            continue
    raise ModuleNotFoundError(f"Module {name} not found!")


def list_tracer() -> Iterator[Tuple[str, str]]:
    """
    List all available tracer
    """
    for possible_path in POSSIBLE_TRACER_PATHS:
        try:
            mod = importlib.import_module(possible_path)
            for k, v in mod.__dict__.items():
                if k.__contains__("Appender") and not k.__contains__("Base"):
                    try:
                        yield k, v.__doc__.strip().splitlines()[0]
                    except AttributeError:
                        yield k, "No docs available"
        except ModuleNotFoundError:
            continue
