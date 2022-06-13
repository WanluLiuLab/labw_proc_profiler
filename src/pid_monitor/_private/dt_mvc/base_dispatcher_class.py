from __future__ import annotations

import gc
import logging
import signal
import threading
import time
from abc import abstractmethod
from typing import Dict, Any, List, Union, Set

from pid_monitor._private import DEFAULT_SYSTEM_INDICATOR_PID, get_timestamp
from pid_monitor._private.dt_mvc.tracer_loader import get_tracer_class


class BaseTracerDispatcherThread(threading.Thread):
    """
    The base class of all dispatchers.
    """
    output_basename: str
    """The report basename."""

    trace_pid: int
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
            trace_pid: int,
            output_basename: str,
            tracers_to_load: tracers_to_load,
            interval: float,
            resolution: float,
            dispatcher_controller: DispatcherController
    ):
        super().__init__()
        self.log_handler = logging.getLogger()
        self.output_basename = output_basename
        self.trace_pid = trace_pid
        self.thread_pool = {}
        self.tracers_to_load = tracers_to_load
        self.interval = interval
        self.resolution = resolution
        self.tracer_kwargs = {
            "output_basename": self.output_basename,
            "interval": self.interval,
            "resolution": self.resolution
        }
        self.should_exit = False
        dispatcher_controller.register_dispatcher(self.trace_pid, self)
        self.dispatcher_controller = dispatcher_controller

    def get_timestamp(self) -> str:
        """
        Get timestamp in an accuracy of 0.01 seconds.
        """
        return get_timestamp(self.resolution)

    def append_threadpool(self, thread: threading.Thread):
        self.thread_pool[thread.__class__.__name__] = thread

    def start_tracers(self):
        """Start loaded tracers. Should be called at the end of :py:func:`init`."""
        for tracer in self.tracers_to_load:
            try:
                self.log_handler.info(f"trace_pid={self.trace_pid}: Fetch TRACER={tracer}")
                new_thread = get_tracer_class(tracer)(**self.tracer_kwargs)
                self.log_handler.info(f"trace_pid={self.trace_pid}: Fetch TRACER={tracer} SUCCESS")
            except Exception as e:
                self.log_handler.error(
                    f"trace_pid={self.trace_pid}: "
                    f"Fetch TRACER={tracer} {e.__class__.__name__} encountered! "
                    f"DETAILS={e.__repr__()}"
                )
                continue
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
        self.log_handler.info(f"Dispatcher for trace_pid={self.trace_pid} SIGTERM")
        self.before_ending()
        self.dispatcher_controller.remove_dispatcher(self.trace_pid)
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
            return f"Dispatcher for {self.trace_pid}"
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
