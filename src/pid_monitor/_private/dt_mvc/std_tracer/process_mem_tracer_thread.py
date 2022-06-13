from typing import TextIO

from pid_monitor._private import get_timestamp
from pid_monitor._private.dt_mvc.base_tracer_class import BaseProcessTracerThread

__all__ = ("ProcessMEMTracerThread",)


class ProcessMEMTracerThread(BaseProcessTracerThread):
    _cached_resident_mem: float

    def __init__(self, **kwargs):
        super().__init__(tracer_type="mem", **kwargs)
        self._cached_resident_mem = -1.0

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'VIRT',
            'RESIDENT',
            'SHARED',
            'TEXT',
            'DATA',
            'SWAP'
        )) + '\n')
        writer.flush()

    def print_body(self, writer: TextIO, **kwargs):
        x = self.process.memory_full_info()
        self._cached_resident_mem = x.rss
        writer.write('\t'.join((
            get_timestamp(),
            str(x.vms),
            str(self._cached_resident_mem),
            str(x.shared),
            str(x.text),
            str(x.data),
            str(x.swap)
        )) + '\n')
        writer.flush()

    def get_cached_resident_mem(self):
        return self._cached_resident_mem
