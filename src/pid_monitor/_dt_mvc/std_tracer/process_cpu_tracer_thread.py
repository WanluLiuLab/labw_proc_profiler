from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessCPUTracerThread",)


class ProcessCPUTracerThread(BaseProcessTracerThread):
    """
    The CPU monitor, monitoring CPU usage (in percent) of a process. Also shows which CPU a process is on.
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
            tracer_type="cpu",
            table_appender_header=[
                'TIME',
                'OnCPU',
                'CPU_PERCENT'
            ]
        )

    def probe(self):
        cpu_percent = self._process.cpu_percent(interval=1)
        if cpu_percent is None:
            return
        on_cpu = self._process.cpu_num()
        self.frontend_cache.cpu_percent = cpu_percent
        self._appender.append([
            self.get_timestamp(),
            cpu_percent,
            on_cpu
        ])
