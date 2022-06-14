from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessChildTracerThread",)


class ProcessChildTracerThread(BaseProcessTracerThread):
    """
    The CHILD monitor. Monitors number of child process and thread of a process.
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
            tracer_type="child",
            table_appender_header=[
                'TIME',
                'CHILD_PROCESS_NUMBER',
                'THREAD_NUMBER'
            ]
        )

    def probe(self):
        self.frontend_cache.num_child_processes = len(self._process.children())
        self.frontend_cache.num_threads = self._process.num_threads()
        self._appender.append([
            self.get_timestamp(),
            self.frontend_cache.num_child_processes,
            self.frontend_cache.num_threads
        ])
