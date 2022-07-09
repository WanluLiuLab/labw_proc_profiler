import glob

from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread

__all__ = ("ProcessNFDTracerThread",)


class ProcessNFDTracerThread(BaseProcessTracerThread):

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
            tracer_type="nfd",
            table_appender_header=[
                'TIME',
                'N_FD'
            ]
        )

    def get_nfd(self) -> int:
        """
        Get a dictionary of file descriptor and its absolute path, will return original fd path if error.

        :return: A dict of [fd, fd_path], None for permission error.
        """
        glob_pattern = f'/proc/{self.trace_pid}/fd/[0-9]*'
        return len(glob.glob(glob_pattern))

    def probe(self):
        try:
            self._appender.append([
                self.get_timestamp(),
                self.get_nfd()
            ])

        except PermissionError:
            self.log_handler.error(f"TRACEE={self.trace_pid}: PermissionError encountered!")
            return
