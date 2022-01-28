"""
std_tracer.py -- All standard tracers

This Python file encodes all standard tracers,
which only depends on psutil or UNIX ProcFS.

Other tracers that may depend on third-party libraries or software is located in other files
under :py:mod:`additional_tracers`.
"""

import glob
import os
from typing import TextIO, Optional, Dict

import psutil

from pid_monitor import get_timestamp
from pid_monitor.dt_base import BaseSystemTracerThread, BaseProcessTracerThread


class SystemCPUTracerThread(BaseSystemTracerThread):
    """
    System-level CPU utilization tracer, traces CPU utilization of all logical cores.
    """

    def __init__(self, **kwargs):
        super().__init__(tracer_type="cpu", **kwargs)

    def print_header(self, writer: TextIO, **kwargs):
        writer.write(
            'TIME' + '\t'
            + '\t'.join([
                f"{x}" for x in range(psutil.cpu_count())
            ])
            + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        writer.write(
            get_timestamp() + '\t'
            + '\t'.join([str(x) for x in psutil.cpu_percent(interval=1, percpu=True)])
            + '\n')


class SystemMEMTracerThread(BaseSystemTracerThread):
    """
    System-level Memory utilization tracer.

    See documents in folder R/system_report.Rmd for more details about, e.g., what CACHED is.
    """

    def __init__(self, **kwargs):
        super().__init__(tracer_type="mem", **kwargs)

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
        writer.write('\t'.join((get_timestamp(),
                                str(x.total),
                                str(x.total - x.available),
                                str(x.buffers),
                                str(x.cached),
                                str(x.shared)
                                )) + '\n')


class SystemSWAPTracerThread(BaseSystemTracerThread):
    """
    System-level SWAP utilization tracer.utilization tracer.utilization tracer.utilization tracer.
    """

    def __init__(self, **kwargs):
        super().__init__(tracer_type="swap", **kwargs)

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'TOTAL',
            'USED'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        x = psutil.swap_memory()
        writer.write('\t'.join((get_timestamp(),
                                str(x.total),
                                str(x.used)
                                )) + '\n')


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


class ProcessMEMTracerThread(BaseProcessTracerThread):

    def __init__(self, **kwargs):
        super().__init__(tracer_type="mem", **kwargs)

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
        writer.write('\t'.join((get_timestamp(),
                                str(x.vms),
                                str(x.rss),
                                str(x.shared),
                                str(x.text),
                                str(x.data),
                                str(x.swap)
                                )) + '\n')
        writer.flush()


class ProcessChildTracerThread(BaseProcessTracerThread):

    def __init__(self, **kwargs):
        super().__init__(tracer_type="child", **kwargs)

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'CHILD_PROCESS_NUMBER',
            'THREAD_NUMBER'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        child = len(self.process.children())
        thread = self.process.num_threads()
        writer.write('\t'.join((get_timestamp(),
                                str(child),
                                str(thread)
                                )) + '\n')


class ProcessSTATTracerThread(BaseProcessTracerThread):

    def __init__(self, **kwargs):
        super().__init__(tracer_type="stat", **kwargs)

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'STAT'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        stat = self.process.status()
        writer.write('\t'.join((get_timestamp(),
                                stat
                                )) + '\n')


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


class ProcessCPUTracerThread(BaseProcessTracerThread):

    def __init__(self, **kwargs):
        super().__init__(tracer_type="cpu", **kwargs)

    def print_header(self, writer: TextIO, **kwargs):
        writer.write('\t'.join((
            'TIME',
            'OnCPU',
            'CPU_PERCENT'
        )) + '\n')

    def print_body(self, writer: TextIO, **kwargs):
        on_cpu = self.process.cpu_num()
        cpu_percent = self.process.cpu_percent(interval=1)
        writer.write('\t'.join((
            get_timestamp(),
            str(on_cpu),
            str(cpu_percent)
        )) + '\n')
