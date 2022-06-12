import logging
import threading
from abc import abstractmethod, ABC
from time import sleep
from typing import TextIO

import psutil

from pid_monitor import PSUTIL_NOTFOUND_ERRORS, DEFAULT_SYSTEM_INDICATOR_PID


class BaseTracerThread(threading.Thread):
    """
    The base class of all tracers.
    """
    output_basename: str
    """The log basename."""

    interval: float
    """Interval of tracing in seconds."""

    tracer_type: str
    """What aspect is being traced? CPU, memory or others?"""

    trace_pid: int
    """What is being traced? DEFAULT_SYSTEM_INDICATOR_PID for System, ``pid`` for processes or threads."""

    should_exit: bool
    """Whether this thread should be terminated"""

    log_handler: logging.Logger
    """The logger handler"""

    def __init__(
            self,
            output_basename: str,
            trace_pid: int,
            tracer_type: str,
            interval
    ):
        super().__init__()
        self.output_basename = output_basename
        self.interval = interval
        self.tracer_type = tracer_type
        self.trace_pid = trace_pid
        self.should_exit = False
        self.log_handler = logging.getLogger()
        self.log_handler.debug(f"Tracer for TRACE_PID={self.trace_pid} TYPE={self.tracer_type} added")

    def run(self):
        self.log_handler.debug(f"Tracer for TRACE_PID={self.trace_pid} TYPE={self.tracer_type} started")
        self.run_body()
        self.log_handler.debug(f"Tracer for TRACE_PID={self.trace_pid} TYPE={self.tracer_type} stopped")

    def run_body(self):
        if self.trace_pid == DEFAULT_SYSTEM_INDICATOR_PID:
            out_file = f"{self.output_basename}.sys.{self.tracer_type}.tsv"
        else:
            out_file = f"{self.output_basename}.{self.trace_pid}.{self.tracer_type}.tsv"
        with open(out_file, 'w') as writer:
            self.print_header(writer)
            writer.flush()
            while not self.should_exit:
                try:
                    self.print_body(writer)
                except PSUTIL_NOTFOUND_ERRORS as e:
                    self.log_handler.error(
                        f"TRACE_PID={self.trace_pid} TYPE={self.tracer_type}: {e.__class__.__name__} encountered!"
                    )
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
            return f"{self.tracer_type} monitor for {self.trace_pid}"
        except AttributeError:
            return "Monitor under construction"

    def __str__(self):
        return repr(self)


class BaseSystemTracerThread(BaseTracerThread, ABC):
    def __init__(
            self,
            output_basename: str,
            tracer_type: str,
            interval
    ):
        super().__init__(
            output_basename=output_basename,
            trace_pid=DEFAULT_SYSTEM_INDICATOR_PID,
            tracer_type=tracer_type,
            interval=interval
        )


class BaseProcessTracerThread(BaseTracerThread, ABC):
    def __init__(
            self,
            trace_pid: int,
            output_basename: str,
            tracer_type: str,
            interval
    ):
        super().__init__(
            output_basename=output_basename,
            trace_pid=trace_pid,
            tracer_type=tracer_type,
            interval=interval
        )
        self.trace_pid = trace_pid
        try:
            self.process = psutil.Process(pid=self.trace_pid)
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(
                f"TRACE_PID={self.trace_pid} TYPE={self.tracer_type}: {e.__class__.__name__} encountered!")
            raise e
