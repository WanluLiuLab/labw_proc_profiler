import psutil

from pid_monitor._dt_mvc.frontend_cache.system_frontend_cache import SystemFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseSystemTracerThread

__all__ = ("SystemMEMTracerThread",)


class SystemMEMTracerThread(BaseSystemTracerThread):
    """
    System-level Memory utilization tracer.

    See documents in folder R/system_report.Rmd for more details about, e.g., what CACHED is.
    """

    def __init__(
            self,
            trace_pid: int,
            pmc: PMConfig,
            frontend_cache: SystemFrontendCache
    ):
        super().__init__(
            pmc=pmc,
            trace_pid=trace_pid,
            frontend_cache=frontend_cache
        )
        self._init_setup_hook(
            tracer_type="mem",
            table_appender_header=[
                'TIME',
                'TOTAL',
                'USED',
                'BUFFERED',
                'CACHED',
                'SHARED'
            ]
        )

    def probe(self):
        x = psutil.virtual_memory()
        if x is None:
            return
        self.frontend_cache.vm_total = x.total
        self.frontend_cache.vm_avail = x.available
        self.frontend_cache.vm_buffered = x.buffers
        self.frontend_cache.vm_shared = x.shared
        self._appender.append([
            self.get_timestamp(),
            x.total,
            x.total - x.available,
            x.buffers,
            x.cached,
            x.shared
        ])
