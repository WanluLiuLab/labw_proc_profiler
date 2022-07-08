from __future__ import annotations

import threading
from time import sleep
from typing import Optional

import psutil

from pid_monitor._dt_mvc import PSUTIL_NOTFOUND_ERRORS
from pid_monitor._dt_mvc.appender import BaseTableAppender, load_table_appender_class
from pid_monitor._dt_mvc.frontend_cache.process_frontend_cache import ProcessFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_dispatcher import BaseTracerDispatcherThread, DispatcherController

_REG_MUTEX = threading.Lock()
"""Mutex for writing registries"""

_DISPATCHER_MUTEX = threading.Lock()
"""Mutex for creating dispatchers for new process/thread"""


def get_total_cpu_time(_p: psutil.Process) -> float:
    """
    Get total CPU time for a process.
    Should return time spent in system mode (aka. kernel mode) and user mode.
    """
    try:
        cpu_time_tuple = _p.cpu_times()
        return cpu_time_tuple.system + cpu_time_tuple.user
    except PSUTIL_NOTFOUND_ERRORS:
        return -1


class ProcessTracerDispatcherThread(BaseTracerDispatcherThread):
    """
    The dispatcher, use to monitor whether a process have initiated a sub-process
    and attach a dispatcher to it if it does so.

    Also initializes and monitors task monitors like :py:class:`TraceIOThread`.
    """

    def before_ending(self):
        pass

    _cached_last_cpu_time: float
    _registry_appender: BaseTableAppender
    process: Optional[psutil.Process]

    def __init__(
            self,
            trace_pid: int,
            pmc: PMConfig,
            dispatcher_controller: DispatcherController,
            registry_appender: BaseTableAppender
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
            pmc=pmc,
            dispatcher_controller=dispatcher_controller
        )
        self.process = None
        self._registry_appender = registry_appender

    def _update_last_cpu_time(self):
        self._cached_last_cpu_time = get_total_cpu_time(self.process)
        self._frontend_cache.cpu_time = self._cached_last_cpu_time
        with open(f"{self.pmc.output_basename}.{self.trace_pid}.cputime", mode='w') as writer:
            writer.write(str(self._cached_last_cpu_time) + '\n')

    def run_body(self):
        """
        The major running part of this function performs following things:

        - Refresh CPU time.
        - Detect whether the process have forked sub-processes.
        - Detect whether the process have created new threads.
        """
        self._cached_last_cpu_time = -1
        try:
            self.process = psutil.Process(self.trace_pid)
            name = self.process.name()
            ppid = self.process.ppid()
            self._write_registry()
            self._write_env()
            self._write_mapfile()
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            self._dispatcher_controller.remove_dispatcher(self.trace_pid)
            raise e

        self._frontend_cache = ProcessFrontendCache(
            name=name,
            ppid=ppid,
            pid=self.trace_pid
        )
        self._dispatcher_controller.register_frontend_cache(
            self.trace_pid,
            self._frontend_cache
        )
        self.start_tracers(
            self.pmc.process_level_tracer_to_load
        )
        while not self.should_exit:
            try:
                with _DISPATCHER_MUTEX:
                    self._detect_process()
                self._update_last_cpu_time()
            except PSUTIL_NOTFOUND_ERRORS:
                break
            sleep(self.pmc.backend_refresh_interval)
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
            self._registry_appender.append([
                self.get_timestamp(),
                self.trace_pid,
                " ".join(self.process.cmdline()),
                self.process.exe(),
                self.process.cwd()
            ])
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def _write_env(self):
        """
        Write initializing environment variables.

        If the process changes its environment variable during execution, it will NOT be recorded!
        """
        try:
            appender = load_table_appender_class(self.pmc.table_appender_type)(
                filename=f"{self.pmc.output_basename}.{self.trace_pid}.env",
                header=["NAME", "VALUE"]
            )
            for env_name, env_value in self.process.environ().items():
                appender.append([env_name, env_value])
            appender.close()
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def _write_mapfile(self):
        """
        Write mapfile information.

        Mapfile information shows how files, especially libraries are stored in memory.
        """
        try:
            appender = load_table_appender_class(self.pmc.table_appender_type)(
                filename=f"{self.pmc.output_basename}.{self.trace_pid}.mapfile",
                header=["PATH", "RESIDENT", "VIRT", "SWAP"]
            )
            for item in self.process.memory_maps():
                appender.append([
                    item.path,
                    item.rss,
                    item.size,
                    item.swap
                ])
            appender.close()
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e

    def _detect_process(self):
        """
        Detect and start child process dispatcher.
        """
        try:
            for process in self.process.children():
                if process.pid not in self._dispatcher_controller.get_current_active_pids():
                    self.log_handler.info(f"Sub-process {process.pid} detected.")
                    new_thread = ProcessTracerDispatcherThread(
                        trace_pid=process.pid,
                        pmc=self.pmc,
                        dispatcher_controller=self._dispatcher_controller,
                        registry_appender=self._registry_appender
                    )
                    new_thread.start()
                    self.append_threadpool(new_thread)
        except PSUTIL_NOTFOUND_ERRORS as e:
            self.log_handler.error(f"TRACEE={self.trace_pid}: {e.__class__.__name__} encountered!")
            raise e
