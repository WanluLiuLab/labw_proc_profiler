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

import multiprocessing
import os
import signal
import subprocess
import sys
import uuid
from collections import namedtuple
from typing import List, Optional

from pid_monitor import main_func

_MONITORED_PROCESS = namedtuple('DefaultProcess', 'pid')(pid=os.getpid())
"""Process being monitored. If monitor not attached, will be myself."""

if os.environ.get('SPHINX_BUILD') == 1:
    exit()


class _PidMonitorProcess(multiprocessing.Process):
    """
    The standalone pid_monitor.main() process.
    """

    def __init__(self, pid: int, output_basename: str):
        super().__init__()
        self.monitored_pid = pid
        self.output_basename = output_basename

    def run(self):
        main_func.main(
            self.monitored_pid,
            os.path.abspath(
                os.path.expanduser(
                    os.path.join(
                        self.output_basename, "proc_profiler", "")
                )
            )
        )


def main(args: Optional[List[str]] = None) -> int:
    """
    :param args: The command-line passed to this module. Should be a list of strings.
                 If not provided, will use `sys.argv[1:]`.
    :return: The return value of ``args``.
    """
    if args is None:
        args = sys.argv[1:]
    if os.environ.get('SPHINX_BUILD') == 1:
        return 0
    global _MONITORED_PROCESS
    for _signal in (
            signal.SIGINT,
            signal.SIGTERM,
            signal.SIGHUP,
            signal.SIGABRT,
            signal.SIGQUIT,
    ):
        signal.signal(_signal, _pass_signal_to_monitored_process)

    print(f'{__doc__.splitlines()[1]} ver. {__version__}')
    print(f'Called by: {" ".join(sys.argv)}')

    output_basename = 'proc_profiler_' + str(uuid.uuid4())
    print(f'Output to: {output_basename}')
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
    pid_monitor_process = _PidMonitorProcess(pid=_MONITORED_PROCESS.pid, output_basename=output_basename)
    pid_monitor_process.start()
    exit_value = _MONITORED_PROCESS.wait()
    pid_monitor_process.join()
    return exit_value


def _pass_signal_to_monitored_process(signal_number: int, *_args):
    global _MONITORED_PROCESS
    try:
        os.kill(_MONITORED_PROCESS.pid, signal_number)
    except ProcessLookupError:
        pass
