from typing import TextIO, List

import psutil

from pid_monitor._private.dt_mvc.base_tracer_class import BaseSystemTracerThread

__all__ = ("SystemCPUTracerThread",)


class SystemCPUTracerThread(BaseSystemTracerThread):
    """
    System-level CPU utilization tracer, traces CPU utilization of all logical cores.
    """

    _cached_cpus_percent: List[float]

    def __init__(self, **kwargs):
        super().__init__(tracer_type="cpu", **kwargs)
        self._cached_cpus_percent = [-0.1]

    def print_header(self, writer: TextIO, **kwargs):
        writer.write(
            'TIME' + '\t'
            + '\t'.join([
                f"{x}" for x in range(psutil.cpu_count())
            ])
            + '\n')

    def get_cached_cpu_percent(self) -> List[float]:
        return self._cached_cpus_percent

    def print_body(self, writer: TextIO, **kwargs):
        self._cached_cpus_percent = psutil.cpu_percent(interval=1, percpu=True)
        writer.write(
            self.get_timestamp() + '\t'
            + '\t'.join(map(str, self._cached_cpus_percent))
            + '\n'
        )
