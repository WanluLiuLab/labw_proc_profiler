# ==============================================================================
#  Copyright (C) 2021-2022. tetgs authors
#
#  This file is a part of tetgs, which is licensed under MIT,
#  a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
#  NAME: proc_profiler -- Process Monitor Utilities
#
#  VERSION HISTORY:
#  2021-08-26 0.1  : Purposed and added by YU Zhejian.
#
# ==============================================================================
"""
proc_profiler -- Process Monitor Utilities

You may use this module in your own project by using its :py:func:`main` function.
"""

__version__ = 0.2

import os
import subprocess
import threading
from typing import List

from pid_monitor import main_func


class _PidMonitorProcess(threading.Thread):
    """
    The standalone pid_monitor.main() process.
    """

    def __init__(self, pid: int, output_basename: str):
        super().__init__()
        self.monitored_pid = pid
        self.output_basename = output_basename

    def run(self):
        main_func.trace_pid(
            toplevel_trace_pid=self.monitored_pid,
            report_basename=os.path.abspath(os.path.expanduser(os.path.join(
                self.output_basename, "proc_profiler", ""
            )))
        )


def run_process(args: List[str], output_basename: str) -> int:
    """
    Runner of the :py:func:`main` function. Can be called by other modules.
    """
    global _MONITORED_PROCESS
    os.makedirs(output_basename)
    try:
        _MONITORED_PROCESS = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=open(os.path.join(output_basename, "proc_profiler.stdout.log"), 'w'),
            stderr=open(os.path.join(output_basename, "proc_profiler.stderr.log"), 'w'),
            close_fds=True
        )
    except FileNotFoundError:
        print("Command not found!")
        return 127
    pid_monitor_process = _PidMonitorProcess(
        pid=_MONITORED_PROCESS.pid,
        output_basename=output_basename
    )
    pid_monitor_process.start()
    exit_value = _MONITORED_PROCESS.wait()
    pid_monitor_process.join()
    return exit_value
