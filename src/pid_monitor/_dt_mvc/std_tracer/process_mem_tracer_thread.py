from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessMEMTracerThread",)


class ProcessMEMTracerThread(BaseProcessTracerThread):
    """
    The process memory usage monitor.
    """

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
            tracer_type="mem",
            table_appender_header=[
                'TIME',
                'VIRT',
                'RESIDENT',
                'SHARED',
                'TEXT',
                'DATA',
                'SWAP'
            ]
        )

    def probe(self):
        x = self._process.memory_full_info()
        if x is None:
            return
        self.frontend_cache.resident_mem = x.rss
        self._appender.append([
            self.get_timestamp(),
            x.vms,
            x.rss,
            x.shared,
            x.text,
            x.data,
            x.swap
        ])
