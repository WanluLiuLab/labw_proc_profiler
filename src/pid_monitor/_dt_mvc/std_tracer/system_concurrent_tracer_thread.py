import psutil

from pid_monitor._dt_mvc.frontend_cache.system_frontend_cache import SystemFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseSystemTracerThread

__all__ = ("SystemConcurrentTracerThread",)


class SystemConcurrentTracerThread(BaseSystemTracerThread):
    """
    System-level CPU utilization tracer, traces CPU utilization of all logical cores.
    """

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
        self._init_setup_hook(
            tracer_type="concurrent",
            table_appender_header=[
                "TIME",
                "NPROC",
                "MONITORED_NPROC"
            ]
        )

    def probe(self):
        self._appender.append([
            self.get_timestamp(),
            len(psutil.pids()),
            len(psutil.Process(self.pmc.toplevel_trace_pid).children(recursive=True))
            # Should be optimized by querying frontend
        ])
