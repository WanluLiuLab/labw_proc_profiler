import logging
import threading
import time

from pid_monitor._dt_mvc.pm_config import PMConfig


class ThreadWithPMC(threading.Thread):
    pmc: PMConfig
    should_exit: bool
    """Whether this thread should be terminated"""

    log_handler: logging.Logger
    """The logger handler"""

    trace_pid: int
    """What is being traced? PID for process, DEFAULT_SYSTEM_INDICATOR_PID for system"""

    def __init__(self, trace_pid: int, pmc: PMConfig):
        super().__init__()
        self.pmc = pmc
        self.trace_pid = trace_pid
        self.should_exit = False
        self.log_handler = logging.getLogger()

    def get_timestamp(self):
        """
        Get timestamp in an accuracy of 0.01 seconds.
        """
        return time.time()
