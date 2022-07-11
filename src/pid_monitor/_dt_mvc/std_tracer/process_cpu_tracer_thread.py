import threading
import time

import psutil

from pid_monitor._dt_mvc import appender, PSUTIL_NOTFOUND_ERRORS
from pid_monitor._dt_mvc.appender import BaseTableAppender
from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessCPUTracerThread",)


class AsyncProcessCPUProbeThread(threading.Thread):
    process: psutil.Process
    appender: BaseTableAppender

    def __init__(self, process: psutil.Process, appender: BaseTableAppender, frontend_cache: ProcessFrontendCache):
        super().__init__()
        self.process = process
        self.appender = appender
        self.frontend_cache = frontend_cache

    def run(self):
        try:
            cpu_percent = self.process.cpu_percent(interval=1)
            if cpu_percent is None:
                return
            on_cpu = self.process.cpu_num()
        except PSUTIL_NOTFOUND_ERRORS:
            return
        self.frontend_cache.cpu_percent = cpu_percent
        self.appender.append([
            time.time(),  # FIXME: Replace with get_timestamp()
            cpu_percent,
            on_cpu
        ])


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
        acp = AsyncProcessCPUProbeThread(
            appender=self._appender,
            process=self._process,
            frontend_cache=self.frontend_cache
        )
        acp.start()
