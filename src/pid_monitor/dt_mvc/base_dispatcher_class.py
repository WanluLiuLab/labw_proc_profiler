from __future__ import annotations

import gc
import logging
import signal
import threading
import time
from abc import abstractmethod
from typing import Dict, Any, List, Union, Set

from pid_monitor import DEFAULT_SYSTEM_INDICATOR_PID
from pid_monitor.dt_mvc.tracer_loader import get_tracer_class


class BaseTracerDispatcherThread(threading.Thread):
    """
    The base class of all dispatchers.
    """
    basename: str
    """The report basename."""

    dispatchee: int
    """What is being traced? PID for process, DEFAULT_SYSTEM_INDICATOR_PID for system"""

    thread_pool: Dict[str, threading.Thread]
    """The tracer Thread, is name -> thread"""

    tracers_to_load: List[str]
    """List[str] of loaded tracers."""

    tracer_kwargs: Dict[str, Any]
    """Dict[str,Any] for tracer options."""

    interval: float
    """Whether this thread should be terminated"""

    should_exit: bool
    """Interval of tracing in seconds."""

    dispatcher_controller: DispatcherController

    def __init__(
            self,
            dispatchee: int,
            basename: str,
            interval: float,
            dispatcher_controller: DispatcherController
    ):
        super().__init__()
        self.log_handler = logging.getLogger()
        self.basename = basename
        self.dispatchee = dispatchee
        self.thread_pool = {}
        self.tracers_to_load = []
        self.interval = interval
        self.tracer_kwargs = {
            "basename": self.basename,
            "interval": self.interval
        }
        self.should_exit = False
        dispatcher_controller.register_dispatcher(self.dispatchee, self)
        self.dispatcher_controller = dispatcher_controller

    def append_threadpool(self, thread: threading.Thread):
        self.thread_pool[thread.__class__.__name__] = thread

    def start_tracers(self):
        """Start loaded tracers. Should be called at the end of :py:func:`init`."""
        for tracer in self.tracers_to_load:
            try:
                self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer}")
                new_thread = get_tracer_class(tracer)(**self.tracer_kwargs)
                self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer} SUCCESS")
            except Exception as e:
                self.log_handler.error(
                    f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer} {e.__class__.__name__} encountered!"
                )
                continue
            new_thread.start()
            self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Start TRACER={tracer}")
            self.append_threadpool(new_thread)

    @abstractmethod
    def before_ending(self):
        """
        Method to call to perform clean exit, like writing logs.
        """
        pass

    def run(self):
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} started")
        self.run_body()
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} stopped")

    @abstractmethod
    def run_body(self):
        """
        The default runner
        """
        pass

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
        - Terminate all threads in ``thread_pool``
        - Suicide.
        """
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} SIGTERM")
        self.before_ending()
        self.dispatcher_controller.remove_dispatcher(self.dispatchee)
        for thread in self.thread_pool.values():
            try:
                thread.should_exit = True
            except AttributeError:
                del thread
        time.sleep(2)
        self.thread_pool.clear()
        gc.collect()

    @abstractmethod
    def collect_information(self) -> Dict[str, Any]:
        """
        Collect process information
        """
        pass

    def __repr__(self):
        try:
            return f"Dispatcher for {self.dispatchee}"
        except AttributeError:
            return "Dispatcher under construction"

    def __str__(self):
        return repr(self)


class DispatcherController:
    dispatchers: Dict[int, BaseTracerDispatcherThread]
    """Dict[pid, Dispatcher] for all active dispatchers"""

    all_pids: Set[int]

    def __init__(self):
        self.dispatchers = {}
        self.all_pids = set()

    def terminate_all_dispatchers(self, _signal: Union[signal.signal, int] = signal.SIGTERM, *_args):
        """
        Send signal to all dispatchers.
        """
        for val in self.dispatchers.values():
            try:
                val.should_exit = True
            except AttributeError:
                del val
        time.sleep(2)
        self.dispatchers.clear()
        gc.collect()

    def get_current_active_pids(self):
        return self.dispatchers.keys()

    def register_dispatcher(self, pid: int, dispatcher: BaseTracerDispatcherThread):
        self.dispatchers[pid] = dispatcher
        self.all_pids.add(pid)

    def collect_all_process_info(self) -> Dict[int, Dict[str, str]]:
        retd = {}
        for d_pid, d_val in self.dispatchers.items():
            if d_pid != DEFAULT_SYSTEM_INDICATOR_PID:
                retd[d_pid] = d_val.collect_information()
        return retd

    def collect_system_info(self) -> Dict[str, str]:
        return self.dispatchers[DEFAULT_SYSTEM_INDICATOR_PID].collect_information()

    def remove_dispatcher(self, pid: int):
        try:
            self.dispatchers.pop(pid)
        except KeyError:
            pass
