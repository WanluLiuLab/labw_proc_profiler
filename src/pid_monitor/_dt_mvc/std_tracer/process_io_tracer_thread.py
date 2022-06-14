from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessIOTracerThread",)


class ProcessIOTracerThread(BaseProcessTracerThread):
    """
    The IO monitor, monitoring the disk and total read/write of a process.
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
            tracer_type="io",
            table_appender_header=[
                'TIME',
                'DiskRead',
                'DiskWrite',
                'TotalRead',
                'TotalWrite'
            ]
        )

    def probe(self):
        io_info = self._process.io_counters()
        if io_info is None:
            return
        curr_dr = io_info.read_bytes
        curr_dw = io_info.write_bytes
        curr_tr = io_info.read_chars
        curr_tw = io_info.write_chars
        self._appender.append([
            self.get_timestamp(),
            curr_dr,
            curr_dw,
            curr_tr,
            curr_tw,
        ])
