import sys

import psutil

from pid_monitor._dt_mvc import PSUTIL_NOTFOUND_ERRORS
from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessCPUTimeTracerThread",)


def get_total_cpu_time(_p: psutil.Process) -> float:
    """
    Get total CPU time for a process.
    Should return time spent in system mode (aka. kernel mode) and user mode.
    """
    try:
        cpu_time_tuple = _p.cpu_times()
        return cpu_time_tuple.system + cpu_time_tuple.user
    except PSUTIL_NOTFOUND_ERRORS:
        return -1


class ProcessCPUTimeTracerThread(BaseProcessTracerThread):
    """
    The CPU time tracer
    """
    _cached_last_cpu_time: float
    _cputime_filename: str

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
        self._init_setup_hook(
            tracer_type="cpu",
            table_appender_header=None
        )
        self._cached_last_cpu_time = -1.0
        self._cputime_filename = f"{self.pmc.output_basename}.{self.trace_pid}.cputime"

    def probe(self):
        self.log_handler.debug(f"DISPATCHEE={self.trace_pid}: update CPUTIME")
        lct = get_total_cpu_time(self._process)
        if lct == -1:
            pass
        else:
            self._cached_last_cpu_time = lct
        self.frontend_cache.cpu_time = self._cached_last_cpu_time
        with open(self._cputime_filename, 'w') as writer:
            writer.write(str(self._cached_last_cpu_time) + '\n')
        self.log_handler.debug(f"DISPATCHEE={self.trace_pid}: update CPUTIME {self._cached_last_cpu_time} SUCCESS")
