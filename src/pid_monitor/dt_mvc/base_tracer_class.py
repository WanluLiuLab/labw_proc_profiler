import logging
import threading
from abc import abstractmethod, ABC
from time import sleep
from typing import TextIO

import psutil

from pid_monitor import DEFAULT_REFRESH_INTERVAL, PSUTIL_NOTFOUND_ERRORS


class BaseTracerThread(threading.Thread):
    """
    The base class of all tracers.
    """
    basename: str
    """The log basename."""

    interval: float
    """Interval of tracing in seconds."""

    tracer_type: str
    """What aspect is being traced? CPU, memory or others?"""

    tracee: str
    """What is being traced? 'sys' for System, `pid` for processes or threads."""

    should_exit: bool
    """Whether this thread should be terminated"""

    log_handler: logging.Logger
    """The logger handler"""

    def __init__(
            self,
            basename: str,
            tracee: str,
            tracer_type: str,
            interval: float = DEFAULT_REFRESH_INTERVAL
    ):
        super().__init__()
        self.basename = basename
        self.interval = interval
        self.tracer_type = tracer_type
        self.tracee = tracee
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
                except PSUTIL_NOTFOUND_ERRORS as e:
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

    def __str__(self):
        return repr(self)


class BaseSystemTracerThread(BaseTracerThread, ABC):
    def __init__(
            self,
            basename: str,
            tracer_type: str,
            interval: float = DEFAULT_REFRESH_INTERVAL
    ):
        super().__init__(
            basename=basename,
            tracee='sys',
            tracer_type=tracer_type,
            interval=interval
        )


class BaseProcessTracerThread(BaseTracerThread, ABC):
    def __init__(
            self,
            trace_pid: int,
            basename: str,
            tracer_type: str,
            interval: float = DEFAULT_REFRESH_INTERVAL
    ):
        super().__init__(
            basename=basename,
            tracee=str(trace_pid),
            tracer_type=tracer_type,
            interval=interval
        )
        self.trace_pid = trace_pid
        try:
            self.process = psutil.Process(pid=self.trace_pid)
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(
                f"TRACEE={self.trace_pid} TYPE={self.tracer_type}: {e.__class__.__name__} encountered!")
            raise e
