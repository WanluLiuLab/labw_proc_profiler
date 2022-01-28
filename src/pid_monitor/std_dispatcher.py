from time import sleep

import psutil

from pid_monitor import _ALL_PIDS, _PSUTIL_NOTFOUND_ERRORS, _DEFAULT_REFRESH_INTERVAL
from pid_monitor import get_timestamp, get_total_cpu_time
from pid_monitor.dt_base import BaseTracerDispatcherThread
from pid_monitor.dt_utils import _DISPATCHERS, _REG_MUTEX, _DISPATCHER_MUTEX
from pid_monitor.frontend import FRONTEND_ALL_PIDS


class ProcessTracerDispatcherThread(BaseTracerDispatcherThread):
    """
    The dispatcher, use to monitor whether a process have initiated a sub-process
    and attach a dispatcher to it if it does so.

    Also initializes and monitors task monitors like :py:class:`TraceIOThread`.
    """

    def __init__(self, trace_pid: int, basename: str, loaded_tracers=None):
        """
        The constructor of the class will do following things:

        - Detech whether this process exists. If not exists, will raise an error.
        - Add PID to all recorded PIDS.
        - Write system-level registry.
        - Write initializing environment variables of this process.
        - Write mapfile information.
        - Start load_tracers.
        """
        super().__init__(str(trace_pid), basename)
        self.loaded_tracers = loaded_tracers
        if self.loaded_tracers is None:
            self.loaded_tracers = (
                "ProcessIOTracerThread",
                "ProcessFDTracerThread",
                "ProcessMEMTracerThread",
                "ProcessChildTracerThread",
                "ProcessCPUTracerThread",
                "ProcessSTATTracerThread",
                "ProcessSyscallTracerThread"
            )
        self.trace_pid = trace_pid

        try:
            self.process = psutil.Process(self.trace_pid)
        except _PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e
        _ALL_PIDS.add(trace_pid)
        self.last_cpu_time = 0
        self.write_registry()
        self.write_env()
        self.write_mapfile()

        self.tracer_kwargs["trace_pid"] = trace_pid
        self.start_tracers()

    def run_body(self):
        """
        The major running part of this function performs following things:

        - Refresh CPU time.
        - Detect whether the process have forked sub-processes.
        - Detect whether the process have created new threads.
        """
        while not self.should_exit:
            try:
                self.last_cpu_time = get_total_cpu_time(self.process)
                with _DISPATCHER_MUTEX:
                    self.detect_process()
            except _PSUTIL_NOTFOUND_ERRORS:
                break
            sleep(_DEFAULT_REFRESH_INTERVAL)
        self.sigterm()

    def write_registry(self):
        """
        Write registry information with following information:

        - Process ID
        - Commandline
        - Executable path
        - Current working directory
        """
        try:
            with _REG_MUTEX:
                with open(f"{self.basename}.reg.tsv", mode='a') as writer:
                    writer.write('\t'.join((
                        get_timestamp(),
                        str(self.trace_pid),
                        " ".join(self.process.cmdline()),
                        self.process.exe(),
                        self.process.cwd()
                    )) + '\n')
                    writer.flush()
        except _PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def write_env(self):
        """
        Write initializing environment variables.

        If the process changes its environment variable during execution, it will NOT be recorded!
        """
        try:
            with open(f"{self.basename}.{self.trace_pid}.env.tsv", mode='w') as writer:
                writer.write('\t'.join(("NAME", "VALUE")) + '\n')
                for env_name, env_value in self.process.environ().items():
                    writer.write('\t'.join((env_name, env_value)) + '\n')
        except _PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def write_mapfile(self):
        """
        Write mapfile information.

        Mapfile information shows how files, especially libraries are stored in memory.
        """
        try:
            with open(f"{self.basename}.{self.trace_pid}.mapfile.tsv", mode='w') as writer:
                writer.write('\t'.join(("PATH", "RESIDENT", "VIRT", "SWAP")) + '\n')
                for item in self.process.memory_maps():
                    writer.write('\t'.join((
                        item.path,
                        str(item.rss),
                        str(item.size),
                        str(item.swap)
                    )) + '\n')
        except _PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def detect_process(self):
        """
        Detect and start child process dispatcher.
        """
        try:
            for process in self.process.children():
                if process.pid not in _DISPATCHERS.keys():
                    self.log_handler.info(f"Sub-process {process.pid} detected.")
                    _DISPATCHERS[process.pid] = ProcessTracerDispatcherThread(process.pid, self.basename)
                    _DISPATCHERS[process.pid].start()
                    self.thread_pool.append(_DISPATCHERS[process.pid])
                    FRONTEND_ALL_PIDS.add(process.pid)
        except _PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def before_ending(self):
        """
        This function performs following things:

        - Record CPU time.
        """
        with open(f"{self.basename}.{self.trace_pid}.cputime", mode='w') as writer:
            writer.write(str(self.last_cpu_time) + '\n')


class SystemTracerDispatcherThread(BaseTracerDispatcherThread):
    """
    The dispatcher, use to monitor whether a process have initiated a sub-process
    and attach a dispatcher to it if it does so.

    Also initializes and monitors task monitors like :py:class:`TraceIOThread`.
    """

    def __init__(self, basename: str, loaded_tracers=None):
        super().__init__(dispatchee="sys", basename=basename)
        self.loaded_tracers = loaded_tracers
        if self.loaded_tracers is None:
            self.loaded_tracers = (
                "SystemMEMTracerThread",
                "SystemCPUTracerThread",
                "SystemSWAPTracerThread"
            )
        self.write_mnt()

        self.start_tracers()

    def write_mnt(self):
        """
        Write mounted volumes to ``mnt.csv``.
        """
        with open(f"{self.basename}.mnt.tsv", mode='w') as writer:
            writer.write('\t'.join((
                "DEVICE",
                "MOUNT_POINT",
                "FSTYPE",
                "OPTS",
                "TOTAL",
                "USED"
            )) + '\n')
            for item in psutil.disk_partitions():
                disk_usage = psutil.disk_usage(item.mountpoint)
                writer.write('\t'.join((
                    item.device,
                    item.mountpoint,
                    item.fstype,
                    item.opts,
                    str(disk_usage.total),
                    str(disk_usage.used)
                )) + '\n')
