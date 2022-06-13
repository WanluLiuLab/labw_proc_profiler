from typing import TextIO, Tuple

import psutil

from pid_monitor._private.dt_mvc.base_tracer_class import BaseSystemTracerThread

__all__ = ("SystemSWAPTracerThread",)


class SystemSWAPTracerThread(BaseSystemTracerThread):
    """
    System-level SWAP utilization tracer.utilization tracer.utilization tracer.utilization tracer.
    """
    _cached_swap_total: int
    _cached_swap_used: int

    def __init__(self, **kwargs):
        super().__init__(tracer_type="swap", **kwargs)
        self._cached_swap_total = -1
        self._cached_swap_used = -1

    def get_cached_swap_info(self) -> Tuple[int, int]:
        return self._cached_swap_total - self._cached_swap_used, self._cached_swap_used

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'TOTAL',
            'USED'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        x = psutil.swap_memory()
        self._cached_swap_total = x.total
        self._cached_swap_used = x.used
        writer.write('\t'.join((
            self.get_timestamp(),
            str(self._cached_swap_total),
            str(self._cached_swap_used)
        )) + '\n')
