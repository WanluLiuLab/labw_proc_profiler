from typing import TextIO

from pid_monitor import get_timestamp
from pid_monitor.dt_mvc.base_tracer_class import BaseProcessTracerThread

__all__ = ("ProcessIOTracerThread",)


class ProcessIOTracerThread(BaseProcessTracerThread):
    """
    The IO monitor, monitoring the disk and total read/write of a process.
    """

    def __init__(self, **kwargs):
        super().__init__(tracer_type="io", **kwargs)

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join([
            'TIME',
            'DiskRead',
            'DiskWrite',
            'TotalRead',
            'TotalWrite'
        ]) + '\n')
        writer.flush()

    def print_body(self, writer: TextIO, **kwargs):
        io_info = self.process.io_counters()
        if io_info is None:
            return
        curr_dr = io_info.read_bytes
        curr_dw = io_info.write_bytes
        curr_tr = io_info.read_chars
        curr_tw = io_info.write_chars
        writer.write('\t'.join([
            get_timestamp(),
            str(curr_dr),
            str(curr_dw),
            str(curr_tr),
            str(curr_tw),
        ]) + '\n')
        writer.flush()
