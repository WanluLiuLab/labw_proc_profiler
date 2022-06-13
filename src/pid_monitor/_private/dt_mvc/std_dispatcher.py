import statistics
import threading
from time import sleep
from typing import Dict, List

import psutil

from pid_monitor._private import PSUTIL_NOTFOUND_ERRORS, DEFAULT_SYSTEM_INDICATOR_PID, get_total_cpu_time, \
    to_human_readable
from pid_monitor._private.dt_mvc.base_dispatcher_class import BaseTracerDispatcherThread, DispatcherController

_REG_MUTEX = threading.Lock()
"""Mutex for writing registries"""

_DISPATCHER_MUTEX = threading.Lock()
"""Mutex for creating dispatchers for new process/thread"""


class ProcessTracerDispatcherThread(BaseTracerDispatcherThread):
    """
    The dispatcher, use to monitor whether a process have initiated a sub-process
    and attach a dispatcher to it if it does so.

    Also initializes and monitors task monitors like :py:class:`TraceIOThread`.
    """

    _cached_last_cpu_time: float

    _frontend_cache: Dict[str, str]

    def collect_information(self) -> Dict[str, str]:
        return self._frontend_cache

    def __init__(
            self,
            trace_pid: int,
            output_basename: str,
            tracers_to_load: List[str],
            interval: float,
            resolution: float,
            dispatcher_controller: DispatcherController
    ):
        """
        The constructor of the class will do following things:

        - Detech whether this process exists. If not exists, will raise an error.
        - Add PID to all recorded PIDS.
        - Write system-level registry.
        - Write initializing environment variables of this process.
        - Write mapfile information.
        - Start load_tracers.
        """
        super().__init__(
            trace_pid=trace_pid,
            output_basename=output_basename,
            tracers_to_load=tracers_to_load,
            interval=interval,
            resolution=resolution,
            dispatcher_controller=dispatcher_controller
        )

        try:
            self.process = psutil.Process(self.trace_pid)
            self._setup_cache()
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

        self._write_registry()
        self._write_env()
        self._write_mapfile()

        self.tracer_kwargs["trace_pid"] = self.trace_pid
        self.start_tracers()

    def run_body(self):
        """
        The major running part of this function performs following things:

        - Refresh CPU time.
        - Detect whether the process have forked sub-processes.
        - Detect whether the process have created new threads.
        """
        while not self.should_exit:
            self._update_cache()
            try:
                with _DISPATCHER_MUTEX:
                    self._detect_process()
            except PSUTIL_NOTFOUND_ERRORS:
                break
            sleep(self.interval)
        self.sigterm()

    def _write_registry(self):
        """
        Write registry information with following information:

        - Process ID
        - Commandline
        - Executable path
        - Current working directory
        """
        try:
            with _REG_MUTEX:
                with open(f"{self.output_basename}.reg.tsv", mode='a') as writer:
                    writer.write('\t'.join((
                        self.get_timestamp(),
                        str(self.trace_pid),
                        " ".join(self.process.cmdline()),
                        self.process.exe(),
                        self.process.cwd()
                    )) + '\n')
                    writer.flush()
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def _write_env(self):
        """
        Write initializing environment variables.

        If the process changes its environment variable during execution, it will NOT be recorded!
        """
        try:
            with open(f"{self.output_basename}.{self.trace_pid}.env.tsv", mode='w') as writer:
                writer.write('\t'.join(("NAME", "VALUE")) + '\n')
                for env_name, env_value in self.process.environ().items():
                    writer.write('\t'.join((env_name, env_value)) + '\n')
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def _write_mapfile(self):
        """
        Write mapfile information.

        Mapfile information shows how files, especially libraries are stored in memory.
        """
        try:
            with open(f"{self.output_basename}.{self.trace_pid}.mapfile.tsv", mode='w') as writer:
                writer.write('\t'.join(("PATH", "RESIDENT", "VIRT", "SWAP")) + '\n')
                for item in self.process.memory_maps():
                    writer.write('\t'.join((
                        item.path,
                        str(item.rss),
                        str(item.size),
                        str(item.swap)
                    )) + '\n')
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def _detect_process(self):
        """
        Detect and start child process dispatcher.
        """
        try:
            for process in self.process.children():
                if process.pid not in self.dispatcher_controller.get_current_active_pids():
                    self.log_handler.info(f"Sub-process {process.pid} detected.")
                    new_thread = ProcessTracerDispatcherThread(
                        trace_pid=process.pid,
                        output_basename=self.output_basename,
                        tracers_to_load=self.tracers_to_load,
                        interval=self.interval,
                        dispatcher_controller=self.dispatcher_controller,
                        resolution=self.resolution
                    )
                    new_thread.start()
                    self.append_threadpool(new_thread)
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def before_ending(self):
        """
        This function performs following things:

        - Record CPU time.
        """
        with open(f"{self.output_basename}.{self.trace_pid}.cputime", mode='w') as writer:
            writer.write(str(self._cached_last_cpu_time) + '\n')

    def _setup_cache(self):
        """
        Setup cached values
        """
        self._cached_last_cpu_time = 0
        self._frontend_cache = {
            "PID": str(self.trace_pid),
            "PPID": "NA",
            "NAME": "NA",
            "CPU%": "NA",
            "STAT": "NA",
            "CPU_TIME": str(self._cached_last_cpu_time),
            "RESIDENT_MEM": "NA",
            "NUM_THREADS": "NA",
            "NUM_CHILD_PROCESS": "NA"
        }

        try:
            self._frontend_cache["NAME"] = self.process.name()
            self._frontend_cache["PPID"] = str(self.process.ppid())
        except PSUTIL_NOTFOUND_ERRORS as e:
            raise e

    def _update_cache(self):
        self._cached_last_cpu_time = max(
            self._cached_last_cpu_time,
            get_total_cpu_time(self.process)
        )
        self._frontend_cache["CPU_TIME"] = str(
            round(self._cached_last_cpu_time, 2)
        )
        if "ProcessCPUTracerThread" in self.thread_pool:
            self._frontend_cache["CPU%"] = str(
                self.thread_pool["ProcessCPUTracerThread"].get_cached_cpu_percent()
            )
        if "ProcessMEMTracerThread" in self.thread_pool:
            self._frontend_cache["RESIDENT_MEM"] = to_human_readable(
                self.thread_pool["ProcessMEMTracerThread"].get_cached_resident_mem()
            )
        if "ProcessChildTracerThread" in self.thread_pool:
            thread_child_process_num = \
                self.thread_pool["ProcessChildTracerThread"].get_cached_thread_child_process_num()
            self._frontend_cache["NUM_THREADS"] = str(
                thread_child_process_num[0]
            )
            self._frontend_cache["NUM_CHILD_PROCESS"] = str(
                thread_child_process_num[1]
            )
        if "STAT" in self.thread_pool:
            self._frontend_cache["STAT"] = self.thread_pool["ProcessSTATTracerThread"].get_cached_stat()


class SystemTracerDispatcherThread(BaseTracerDispatcherThread):
    """
    The dispatcher, use to monitor whether a process have initiated a sub-process
    and attach a dispatcher to it if it does so.

    Also initializes and monitors task monitors like :py:class:`TraceIOThread`.
    """

    _frontend_cache: Dict[str, str]

    def _setup_cache(self):
        self._frontend_cache = {
            "CPU%": "NA",
            "VM_AVAIL": "NA",
            "VM_TOTAL": "NA",
            "VM_PERCENT": "NA",
            "BUFFERED": "NA",
            "SHARED": "NA",
            "SWAP_AVAIL": "NA",
            "SWAP_TOTAL": "NA",
            "SWAP_PERCENT": "NA"
        }

    def before_ending(self):
        """Disabled"""
        pass

    def collect_information(self) -> Dict[str, str]:
        return self._frontend_cache

    def __init__(
            self,
            basename: str,
            tracers_to_load: List[str],
            interval: float,
            resolution: float,
            dispatcher_controller: DispatcherController
    ):
        super().__init__(
            trace_pid=DEFAULT_SYSTEM_INDICATOR_PID,
            output_basename=basename,
            tracers_to_load=tracers_to_load,
            interval=interval,
            resolution=resolution,
            dispatcher_controller=dispatcher_controller
        )
        self._setup_cache()
        self._write_mnt()
        self.start_tracers()

    def run_body(self):
        while not self.should_exit:
            self._update_cache()
            sleep(self.interval)

    def _write_mnt(self):
        """
        Write mounted volumes to ``mnt.csv``.
        """
        with open(f"{self.output_basename}.mnt.tsv", mode='w') as writer:
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

    def _update_cache(self):
        if "SystemCPUTracerThread" in self.thread_pool:
            self._frontend_cache["CPU%"] = str(round(
                statistics.mean(self.thread_pool["SystemCPUTracerThread"].get_cached_cpu_percent()), 2
            )) + "%"
        if "SystemMEMTracerThread" in self.thread_pool:
            mem_info = self.thread_pool["SystemMEMTracerThread"].get_cached_vm_info()
            self._frontend_cache["VM_AVAIL"] = to_human_readable(mem_info[0])
            self._frontend_cache["VM_TOTAL"] = to_human_readable(mem_info[1])
            if mem_info[1] != 0:
                self._frontend_cache["VM_PERCENT"] = str(round(mem_info[0] / mem_info[1] * 100, 2)) + "%"
            else:
                self._frontend_cache["VM_PERCENT"] = "0.00%"
            self._frontend_cache["BUFFERED"] = to_human_readable(mem_info[2])
            self._frontend_cache["SHARED"] = to_human_readable(mem_info[3])
        if "SystemSWAPTracerThread" in self.thread_pool:
            swap_info = self.thread_pool["SystemSWAPTracerThread"].get_cached_swap_info()
            self._frontend_cache["SWAP_AVAIL"] = to_human_readable(swap_info[0])
            self._frontend_cache["SWAP_TOTAL"] = to_human_readable(swap_info[1])
            if swap_info[1] != 0:
                self._frontend_cache["SWAP_PERCENT"] = str(round(swap_info[0] / swap_info[1] * 100, 2)) + "%"
            else:
                self._frontend_cache["SWAP_PERCENT"] = "0.00%"
