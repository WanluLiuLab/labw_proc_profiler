import psutil

from pid_monitor._dt_mvc import DEFAULT_SYSTEM_INDICATOR_PID
from pid_monitor._dt_mvc.appender import load_table_appender_class
from pid_monitor._dt_mvc.appender.typing import TableAppenderConfig
from pid_monitor._dt_mvc.frontend_cache.system_frontend_cache import SystemFrontendCache
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_dispatcher import BaseTracerDispatcherThread, DispatcherController


class SystemTracerDispatcherThread(BaseTracerDispatcherThread):
    """
    The dispatcher, use to monitor whether a process have initiated a sub-process
    and attach a dispatcher to it if it does so.

    Also initializes and monitors task monitors like :py:class:`TraceIOThread`.
    """

    def before_ending(self):
        """Disabled"""
        pass

    def __init__(
            self,
            pmc: PMConfig,
            dispatcher_controller: DispatcherController
    ):
        super().__init__(
            trace_pid=DEFAULT_SYSTEM_INDICATOR_PID,
            pmc=pmc,
            dispatcher_controller=dispatcher_controller
        )

    def run_body(self):
        self._write_mnt()
        self._frontend_cache = SystemFrontendCache()
        self._dispatcher_controller.register_frontend_cache(
            self.trace_pid,
            self._frontend_cache
        )
        self.start_tracers(
            self.pmc.system_level_tracers_to_load
        )

    def _write_mnt(self):
        """
        Write mounted volumes to ``mnt.csv``.
        """
        appender = load_table_appender_class(self.pmc.table_appender_type)(
            filename=f"{self.pmc.output_basename}.mnt",
            header=[
                "DEVICE",
                "MOUNT_POINT",
                "FSTYPE",
                "OPTS",
                "TOTAL",
                "USED"
            ],
            tac=TableAppenderConfig(
                self.pmc.table_appender_buffer_size
            )
        )
        for item in psutil.disk_partitions():
            disk_usage = psutil.disk_usage(item.mountpoint)
            appender.append([
                item.device,
                item.mountpoint,
                item.fstype,
                item.opts,
                disk_usage.total,
                disk_usage.used
            ])
        appender.close()
