import psutil

from pid_monitor._dt_mvc.frontend_cache.system_frontend_cache import SystemFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseSystemTracerThread

__all__ = ("SystemSWAPTracerThread",)


class SystemSWAPTracerThread(BaseSystemTracerThread):
    """
    System-level SWAP utilization tracer.utilization tracer.utilization tracer.utilization tracer.
    """

    def __init__(
            self,
            pmc: PMConfig,
            trace_pid: int,
            frontend_cache: SystemFrontendCache
    ):
        super().__init__(
            pmc=pmc,
            trace_pid=trace_pid,
            frontend_cache=frontend_cache
        )
        self._init_setup_hook(
            tracer_type="swap",
            table_appender_header=[
                'TIME',
                'TOTAL',
                'USED'
            ]
        )

    def probe(self):
        x = psutil.swap_memory()
        if x is None:
            return
        self.frontend_cache.swap_total = x.total
        self.frontend_cache.swap_used = x.used
        self._appender.append([
            self.get_timestamp(),
            x.total,
            x.used
        ])
