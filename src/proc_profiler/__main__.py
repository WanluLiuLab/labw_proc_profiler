import os
import signal
import sys
import uuid
from collections import namedtuple

from pid_monitor import __version__
from proc_profiler import run_process

_MONITORED_PROCESS = namedtuple('DefaultProcess', 'pid')(pid=os.getpid())
"""Process being monitored. If monitor not attached, will be myself."""

if os.environ.get('SPHINX_BUILD') == 1:
    exit()


def _pass_signal_to_monitored_process(signal_number: int, *_args):
    global _MONITORED_PROCESS
    try:
        os.kill(_MONITORED_PROCESS.pid, signal_number)
    except ProcessLookupError:
        pass


if __name__ == "__main__":
    args = sys.argv[1:]
    if os.environ.get('SPHINX_BUILD') == 1:
        exit(0)
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
    print(f'Output to: {os.path.join(os.getcwd(), output_basename)}')
    exit(run_process(args, output_basename))
