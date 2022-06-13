from typing import TextIO, Tuple

import psutil

from pid_monitor._private.dt_mvc.base_tracer_class import BaseSystemTracerThread

__all__ = ("SystemMEMTracerThread",)


class SystemMEMTracerThread(BaseSystemTracerThread):
    """
    System-level Memory utilization tracer.

    See documents in folder R/system_report.Rmd for more details about, e.g., what CACHED is.
    """
    _cached_vm_avail: int
    _cached_vm_total: int
    _cached_vm_buffered: int
    _cached_vm_shared: int

    def __init__(self, **kwargs):
        super().__init__(tracer_type="mem", **kwargs)
        self._cached_vm_avail = -1
        self._cached_vm_total = -1
        self._cached_vm_buffered = -1
        self._cached_vm_shared = -1

    def get_cached_vm_info(self) -> Tuple[int, int, int, int]:
        return (
            self._cached_vm_avail,
            self._cached_vm_total,
            self._cached_vm_buffered,
            self._cached_vm_shared
        )

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'TOTAL',
            'USED',
            'BUFFERED',
            'CACHED',
            'SHARED'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        x = psutil.virtual_memory()
        self._cached_vm_total = x.total
        self._cached_vm_avail = x.available
        self._cached_vm_buffered = x.buffers
        self._cached_vm_shared = x.shared
        writer.write('\t'.join((
            self.get_timestamp(),
            str(self._cached_vm_total),
            str(x.total - self._cached_vm_avail),
            str(self._cached_vm_buffered),
            str(x.cached),
            str(self._cached_vm_shared)
        )) + '\n')
