from typing import TextIO

from pid_monitor import get_timestamp
from pid_monitor.dt_mvc.base_tracer_class import BaseProcessTracerThread

__all__ = ("ProcessSTATTracerThread",)


class ProcessSTATTracerThread(BaseProcessTracerThread):
    _cached_stat: str

    def __init__(self, **kwargs):
        super().__init__(tracer_type="stat", **kwargs)
        self._cached_stat = "NA"

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'STAT'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        self._cached_stat = self.process.status()
        writer.write('\t'.join((
            get_timestamp(),
            self._cached_stat
        )) + '\n')

    def get_cached_stat(self) -> str:
        return self._cached_stat
