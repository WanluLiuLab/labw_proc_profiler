from typing import TextIO, Tuple

from pid_monitor._private import get_timestamp
from pid_monitor._private.dt_mvc.base_tracer_class import BaseProcessTracerThread

__all__ = ("ProcessChildTracerThread",)


class ProcessChildTracerThread(BaseProcessTracerThread):
    _cached_child_process_number: int
    _cached_thread_number: int

    def __init__(self, **kwargs):
        super().__init__(tracer_type="child", **kwargs)
        self._cached_thread_number = -1
        self._cached_child_process_number = -1

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'CHILD_PROCESS_NUMBER',
            'THREAD_NUMBER'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        self._cached_child_process_number = len(self.process.children())
        self._cached_thread_number = self.process.num_threads()
        writer.write('\t'.join((
            get_timestamp(),
            str(self._cached_child_process_number),
            str(self._cached_thread_number)
        )) + '\n')

    def get_cached_thread_child_process_num(self) -> Tuple[int, int]:
        return self._cached_thread_number, self._cached_child_process_number
