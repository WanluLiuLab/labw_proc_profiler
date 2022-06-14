"""
std_tracer -- All standard tracers

This Python file encodes all standard tracers,
which only depends on psutil or UNIX ProcFS.

Other tracers that may depend on third-party libraries or software is located in other files
under :py:mod:`additional_tracer`.
"""
from abc import abstractmethod, ABC
from time import sleep
from typing import Union, Optional, List

import psutil

from pid_monitor._dt_mvc import DEFAULT_SYSTEM_INDICATOR_PID, PSUTIL_NOTFOUND_ERRORS
from pid_monitor._dt_mvc.appender import BaseTableAppender, load_table_appender_class
from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.frontend_cache.system_frontend_cache import SystemFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.typing import ThreadWithPMC


class BaseTracerThread(ThreadWithPMC):
    """
    The base class of all tracers.
    """

    tracer_type: str
    """What aspect is being traced? CPU, memory or others?"""

    _appender: Optional[BaseTableAppender]

    def _init_setup_hook(
            self,
            tracer_type: str,
            table_appender_header: List[str]
    ):
        self.tracer_type = tracer_type
        if self.trace_pid == DEFAULT_SYSTEM_INDICATOR_PID:
            filename = f"{self.pmc.output_basename}.sys.{self.tracer_type}"
        else:
            filename = f"{self.pmc.output_basename}.{self.trace_pid}.{self.tracer_type}"
        self._appender = load_table_appender_class(
            self.pmc.table_appender_type
        )(
            filename=filename,
            header=table_appender_header
        )
        self.log_handler.debug(f"Tracer for TRACE_PID={self.trace_pid} TYPE={self.tracer_type} added")

    def __init__(
            self,
            trace_pid: int,
            pmc: PMConfig,
            frontend_cache: Union[ProcessFrontendCache, SystemFrontendCache]
    ):
        super().__init__(pmc=pmc, trace_pid=trace_pid)
        self.frontend_cache = frontend_cache

    def run(self):
        self.log_handler.debug(f"Tracer for TRACE_PID={self.trace_pid} TYPE={self.tracer_type} started")
        self.run_body()
        self.log_handler.debug(f"Tracer for TRACE_PID={self.trace_pid} TYPE={self.tracer_type} stopped")

    def run_body(self):
        while not self.should_exit:
            try:
                self.probe()
            except PSUTIL_NOTFOUND_ERRORS as e:
                self.log_handler.error(
                    f"TRACE_PID={self.trace_pid} TYPE={self.tracer_type}: {e.__class__.__name__} encountered!"
                )
                return
            sleep(self.pmc.backend_refresh_interval)

    @abstractmethod
    def probe(self):
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
            trace_pid: int,
            pmc: PMConfig,
            frontend_cache: SystemFrontendCache
    ):
        super().__init__(
            trace_pid=trace_pid,
            pmc=pmc,
            frontend_cache=frontend_cache
        )


class BaseProcessTracerThread(BaseTracerThread, ABC):
    _process: psutil.Process

    def __init__(
            self,
            trace_pid: int,
            pmc: PMConfig,
            frontend_cache: ProcessFrontendCache
    ):
        super().__init__(
            trace_pid=trace_pid,
            pmc=pmc,
            frontend_cache=frontend_cache
        )
        self.trace_pid = trace_pid
        try:
            self._process = psutil.Process(pid=self.trace_pid)
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(
                f"TRACE_PID={self.trace_pid} TYPE={self.tracer_type}: {e.__class__.__name__} encountered!")
            raise e
