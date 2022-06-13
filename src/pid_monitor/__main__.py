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

from pid_monitor import __version__
from pid_monitor._private import libfrontend

if __name__ == '__main__':
    libfrontend.setup_frontend(
        "pid_monitor.main",
        "",
        __version__,
        ""
    )
