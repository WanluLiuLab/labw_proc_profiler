import os
import signal
import subprocess
import threading
import uuid
from collections import namedtuple
from typing import List, Any, Mapping, Tuple

from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor.main import trace_pid

_MONITORED_PROCESS = namedtuple('DefaultProcess', 'pid')(pid=os.getpid())
"""Process being monitored. If monitor not attached, will be myself."""


class _PidMonitorProcess(threading.Thread):
    """
    The standalone pid_monitor.main() process.
    """
    monitored_pid: int
    """PID being monitored"""

    output_basename: str
    """Basename of logs"""

    pid_monitor_kwargs: Mapping[str, Any]
    """Arguments to ``trace_pid``"""

    def __init__(self, pid: int, output_basename: str, pid_monitor_kwargs):
        super().__init__()
        self.monitored_pid = pid
        self.output_basename = output_basename
        self.pid_monitor_kwargs = pid_monitor_kwargs

    def run(self):
        trace_pid.trace_pid(PMConfig(
            toplevel_trace_pid=self.monitored_pid,
            output_basename=os.path.abspath(os.path.expanduser(os.path.join(
                self.output_basename, "proc_profiler", ""
            ))))
        )


def run_process(
        cmd: List[str],
        output_basename: str,
        pid_monitor_kwargs=None
) -> int:
    """
    Runner of the :py:func:`main` function. Can be called by other modules.
    """
    if pid_monitor_kwargs is None:
        pid_monitor_kwargs = {}
    global _MONITORED_PROCESS
    os.makedirs(output_basename)
    try:
        _MONITORED_PROCESS = subprocess.Popen(
            args=cmd,
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
        output_basename=output_basename,
        pid_monitor_kwargs=pid_monitor_kwargs
    )
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


def _parse_args(args: List[str]) -> Tuple[Mapping[str, Any], List[str]]:
    """TODO"""
    return {}, args


def main(args: List[str]):
    if os.environ.get('SPHINX_BUILD') == 1:
        return 0
    for _signal in (
            signal.SIGINT,
            signal.SIGTERM,
            signal.SIGHUP,
            signal.SIGABRT,
            signal.SIGQUIT,
    ):
        signal.signal(_signal, _pass_signal_to_monitored_process)

    pid_monitor_kwargs, cmd = _parse_args(args)

    output_basename = "_".join((
        'proc_profiler',
        os.path.basename(cmd[0]),
        str(uuid.uuid4())
    ))
    print(f'Output to: {os.path.join(os.getcwd(), output_basename)}')
    exit(run_process(cmd, output_basename, pid_monitor_kwargs))
