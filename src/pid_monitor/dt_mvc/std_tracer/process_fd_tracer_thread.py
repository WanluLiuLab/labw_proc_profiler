import glob
import os
from typing import TextIO, Optional, Dict

from pid_monitor import get_timestamp
from pid_monitor.dt_mvc.base_tracer_class import BaseProcessTracerThread

__all__ = ("ProcessFDTracerThread",)


class ProcessFDTracerThread(BaseProcessTracerThread):
    def __init__(self, **kwargs):
        super().__init__(tracer_type="fd", **kwargs)

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'FD',
            'Path'
        )) + '\n')

    def get_full_fd_linux(self) -> Optional[Dict[int, str]]:
        """
        Get a dictionary of file descriptor and its absolute path, will return original fd path if error.

        :return: A dict of [fd, fd_path], None for permission error.
        """
        retd = {}
        filename = f'/proc/{self.trace_pid}/fd/[0-9]*'
        try:
            for item in glob.glob(filename):
                try:
                    retd[int(os.path.basename(item))] = os.path.realpath(item)
                except FileNotFoundError:
                    if not os.path.exists(item):
                        self.log_handler.error(f"TRACEE={self.trace_pid}: FileNotFoundError encountered!")
                        retd[int(os.path.basename(item))] = "Non-Exist Path"
                    retd[int(os.path.basename(item))] = item
        except PermissionError:
            self.log_handler.error(f"TRACEE={self.trace_pid}: PermissionError encountered!")
            return None
        return retd

    def print_body(self, writer: TextIO, **kwargs):
        fd = self.get_full_fd_linux()
        if fd is None:
            return
        for key, value in fd.items():
            writer.write('\t'.join((
                get_timestamp(),
                str(key),
                value
            )) + '\n')
