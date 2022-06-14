from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessSTATTracerThread",)


class ProcessSTATTracerThread(BaseProcessTracerThread):
    _cached_stat: str

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
            tracer_type="stat",
            table_appender_header=[
                'TIME',
                'STAT'
            ]
        )

    def probe(self):
        stat = self._process.status()
        if stat is None:
            return
        self.frontend_cache = stat
        self._appender.append([
            self.get_timestamp(),
            stat
        ])
