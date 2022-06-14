import psutil

from pid_monitor._dt_mvc import DEFAULT_SYSTEM_INDICATOR_PID
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
        self._write_mnt()
        self._frontend_cache = SystemFrontendCache()
        self._dispatcher_controller.register_frontend_cache(
            self.trace_pid,
            self._frontend_cache
        )
        self.start_tracers(
            pmc.system_level_tracers_to_load
        )

    def _write_mnt(self):
        """
        Write mounted volumes to ``mnt.csv``.
        """
        with open(f"{self.pmc.output_basename}.mnt.tsv", mode='w') as writer:
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
