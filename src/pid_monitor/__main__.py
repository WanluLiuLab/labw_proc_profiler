# ==============================================================================
#  Copyright (C) 2021-2022. gpmf authors
#
#  This file is a part of tetgs, which is licensed under MIT,
#  a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
#  NAME: proc_monitor.py -- Process Monitor
#
#  VERSION HISTORY:
#  2021-08-26 0.1  : Migrated from LinuxMiniPrograms.
#
# ==============================================================================
"""
Frontend of pid_monitor.

See compiled Sphinx documentations for usage.
"""

import argparse
import logging
import sys

import pid_monitor
from pid_monitor import __version__
from pid_monitor.dt_utils import list_tracer
from pid_monitor.main_func import main

_LOG_HANDLER = logging.getLogger()
"""The Logger Handler"""


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", help="the process ID to attach", required=False, type=int)
    parser.add_argument("-o", "--out", help="the output basename", required=False, type=str)
    parser.add_argument("-l", "--list_tracer", help="List all available tracers", required=False, action="store_true",
                        default=False)
    return parser.parse_args()


if __name__ == '__main__':
    _LOG_HANDLER.setLevel(logging.INFO)
    print(f'{pid_monitor.__doc__.splitlines()[1]} ver. {__version__}')
    print(f'Called by: {" ".join(sys.argv)}')
    args = _parse_args()
    if args.list_tracer:
        for tracer in list_tracer():
            print(tracer[0], ":", tracer[1])
        sys.exit(0)

    sys.exit(main(args.pid, args.out))
