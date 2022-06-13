import os
import signal
import subprocess
import sys
import threading
import uuid
from collections import namedtuple
from typing import List

from pid_monitor import __version__
from pid_monitor.main import trace_pid


class _PidMonitorProcess(threading.Thread):
    """
    The standalone pid_monitor.main() process.
    """

    def __init__(self, pid: int, output_basename: str):
        super().__init__()
        self.monitored_pid = pid
        self.output_basename = output_basename

    def run(self):
        trace_pid.trace_pid(
            toplevel_trace_pid=self.monitored_pid,
            output_basename=os.path.abspath(os.path.expanduser(os.path.join(
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


_MONITORED_PROCESS = namedtuple('DefaultProcess', 'pid')(pid=os.getpid())


def _pass_signal_to_monitored_process(signal_number: int, *_args):
    global _MONITORED_PROCESS
    try:
        os.kill(_MONITORED_PROCESS.pid, signal_number)
    except ProcessLookupError:
        pass


args = sys.argv[1:]
output_basename = 'proc_profiler_' + str(uuid.uuid4())

"""Process being monitored. If monitor not attached, will be myself."""

if os.environ.get('SPHINX_BUILD') == 1:
    exit()

if __name__ == "__main__":
    if os.environ.get('SPHINX_BUILD') == 1:
        exit(0)
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

    print(f'Output to: {os.path.join(os.getcwd(), output_basename)}')
    exit(run_process(args, output_basename))
