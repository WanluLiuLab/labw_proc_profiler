import glob
import os
from typing import Iterable, Tuple

from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_tracer import BaseProcessTracerThread, ProbeError

__all__ = ("ProcessFDTracerThread",)


class ProcessFDTracerThread(BaseProcessTracerThread):

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
            tracer_type="fd",
            table_appender_header=[
                'TIME',
                'FD',
                'Path'
            ]
        )

    def iter_full_fd_linux(self) -> Iterable[Tuple[int, str]]:
        """
        Get a dictionary of file descriptor and its absolute path, will return original fd path if error.

        :return: A dict of [fd, fd_path], None for permission error.
        """
        glob_pattern = f'/proc/{self.trace_pid}/fd/[0-9]*'

        for item in glob.glob(glob_pattern):
            try:
                yield int(os.path.basename(item)), os.path.realpath(item)
            except FileNotFoundError:
                if not os.path.exists(item):
                    self.log_handler.error(f"TRACEE={self.trace_pid}: FileNotFoundError encountered at {item}!")
                yield int(os.path.basename(item)), item

    def probe(self):
        try:
            for fd, path in self.iter_full_fd_linux():
                self._appender.append([
                    self.get_timestamp(),
                    fd,
                    path
                ])
        except PermissionError:
            raise ProbeError(f"TRACEE={self.trace_pid}: PermissionError encountered!")
