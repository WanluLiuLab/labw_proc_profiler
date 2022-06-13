from typing import TextIO

from pid_monitor._private.dt_mvc.base_tracer_class import BaseProcessTracerThread

__all__ = ("ProcessCPUTracerThread",)


class ProcessCPUTracerThread(BaseProcessTracerThread):
    _cached_cpu_percent: float
    _cached_on_cpu: int

    def __init__(self, **kwargs):
        super().__init__(tracer_type="cpu", **kwargs)
        self._cached_cpu_percent = -1.0
        self._cached_on_cpu = -1

    def get_cached_cpu_percent(self):
        return self._cached_cpu_percent

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'OnCPU',
            'CPU_PERCENT'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        self._cached_on_cpu = self.process.cpu_num()
        self._cached_cpu_percent = self.process.cpu_percent(interval=1)
        writer.write('\t'.join((
            self.get_timestamp(),
            str(self._cached_on_cpu),
            str(self._cached_cpu_percent)
        )) + '\n')
