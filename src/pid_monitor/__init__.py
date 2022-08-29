# ==============================================================================
#  Copyright (C) 2021-2022. tetgs authors
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
pid_monitor -- A General-Purposed Python-Implemented Process Monitor

This is a monitor implemented in UNIX ProcFS and :py:mod:`psutils`.
This module should work on any GNU/Linux distributions that have above modules.

To use this module as an **executable**, see :py:mod:`__main__`.

To use this module in your own project, see :py:mod:`main_func`.
"""

from __future__ import annotations

__version__ = "0.3.2"

import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="tracer.log",
    filemode="w",
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s: %(message)s'
)
