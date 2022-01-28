"""
dt_base.py -- Base class for Tracers and Dispatchers

Here you may find all Base class of Tracers and Dispatchers in system/process/tread level.
"""
import gc
import logging
import threading
import time
from abc import abstractmethod
from time import sleep
from typing import TextIO

import psutil

from pid_monitor import _DEFAULT_REFRESH_INTERVAL, _PSUTIL_NOTFOUND_ERRORS
from pid_monitor.dt_utils import get_tracer


class BaseTracerThread(threading.Thread):
    """
    The base class of all tracers.
    """

    def __init__(self, basename: str, tracee: str, tracer_type: str, interval: float = _DEFAULT_REFRESH_INTERVAL):
        super().__init__()
        self.basename = basename
        """The log basename."""

        self.interval = interval
        """Interval of tracing i n seconds."""

        self.tracer_type = tracer_type
        """What aspect is being traced? CPU, memory or others?"""

        self.tracee = tracee
        """What is being traced? 'sys' for System, `pid` for processes or threads."""

        self.should_exit = False

        self.log_handler = logging.getLogger()
        self.log_handler.debug(f"Tracer for TRACEE={self.tracee} TYPE={self.tracer_type} added")

    def run(self):
        self.log_handler.debug(f"Tracer for TRACEE={self.tracee} TYPE={self.tracer_type} started")
        self.run_body()
        self.log_handler.debug(f"Tracer for TRACEE={self.tracee} TYPE={self.tracer_type} stopped")

    def run_body(self):
        out_file = f"{self.basename}.{self.tracee}.{self.tracer_type}.tsv"
        with open(out_file, 'w') as writer:
            self.print_header(writer)
            writer.flush()
            while not self.should_exit:
                try:
                    self.print_body(writer)
                except _PSUTIL_NOTFOUND_ERRORS as e:
                    self.log_handler.error(
                        f"TRACEE={self.tracee} TYPE={self.tracer_type}: {e.__class__.__name__} encountered!")
                    return
                writer.flush()
                sleep(self.interval)

    @abstractmethod
    def print_header(self, writer: TextIO, *args, **kwargs):
        pass

    @abstractmethod
    def print_body(self, writer: TextIO, *args, **kwargs):
        pass

    def __repr__(self):
        try:
            return f"{self.tracer_type} monitor for {self.tracee}"
        except AttributeError:
            return "Monitor under construction"

    __str__ = __repr__


class BaseSystemTracerThread(BaseTracerThread):
    def __init__(self, basename: str, tracer_type: str, interval: float = _DEFAULT_REFRESH_INTERVAL):
        super().__init__(basename=basename, tracee='sys', tracer_type=tracer_type, interval=interval)


class BaseProcessTracerThread(BaseTracerThread):
    def __init__(self, trace_pid: int, basename: str, tracer_type: str, interval: float = _DEFAULT_REFRESH_INTERVAL):
        super().__init__(basename=basename, tracee=str(trace_pid), tracer_type=tracer_type, interval=interval)
        self.trace_pid = trace_pid
        try:
            self.process = psutil.Process(pid=self.trace_pid)
        except _PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(
                f"TRACEE={self.trace_pid} TYPE={self.tracer_type}: {e.__class__.__name__} encountered!")
            raise e


class BaseTracerDispatcherThread(threading.Thread):
    """
    The base class of all dispatchers.
    """

    def __init__(self, dispatchee: str, basename: str):
        super().__init__()
        self.log_handler = logging.getLogger()
        self.basename = basename
        """The report basename."""

        self.dispatchee = dispatchee
        """What is being traced? PID for process, ``sys`` for system"""

        self.thread_pool = []
        """The tracer Thread"""

        self.loaded_tracers = []
        """List[str] of loaded tracers."""

        self.tracer_kwargs = {}
        """Dict[str,Any] for tracer options."""

        self.tracer_kwargs["basename"] = self.basename

        self.should_exit = False

    def start_tracers(self):
        """Start loaded tracers. Should be called at the end of :py:func:`init`."""
        for tracer in self.loaded_tracers:
            try:
                self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer}")
                new_thread = get_tracer(tracer)(**self.tracer_kwargs)
                self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer} SUCCESS")
            except Exception as e:
                self.log_handler.error(
                    f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer} {e.__class__.__name__} encountered!"
                )
                continue
            new_thread.start()
            self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Start TRACER={tracer}")
            self.thread_pool.append(new_thread)

    def before_ending(self):
        """
        Method to call to perform clean exit, like writing logs.
        """
        pass

    def run(self):
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} started")
        self.run_body()
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} stopped")

    def run_body(self):
        """
        The default runner
        """
        while not self.should_exit:
            sleep(_DEFAULT_REFRESH_INTERVAL)

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
        for thread in self.thread_pool:
            try:
                thread.should_exit = True
            except AttributeError:
                del thread
        time.sleep(2)
        self.thread_pool.clear()
        gc.collect()

    def __repr__(self):
        try:
            return f"Dispatcher for {self.dispatchee}"
        except AttributeError:
            return "Dispatcher under construction"

    __str__ = __repr__
