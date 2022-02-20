"""
This module contains main function of pid_monitor and can be used in other projects.
"""

import logging
import os
import signal
import sys

from pid_monitor import _ALL_PIDS, PSUTIL_NOTFOUND_ERRORS
from pid_monitor.dt_utils import terminate_all_dispatchers, _DISPATCHERS
from pid_monitor.frontend import show_frontend
from pid_monitor.report import make_all_report
from pid_monitor.std_dispatcher import SystemTracerDispatcherThread, ProcessTracerDispatcherThread

_LOG_HANDLER = logging.getLogger()
"""The Logger Handler"""


def main(toplevel_trace_pid: int, report_basename: str) -> int:
    """
    The main entrance point

    You may use this function in your own projects.

    :param toplevel_trace_pid: The process ID to trace.
    :param report_basename: Basename of the report.
    :return: 0 for success.
    """
    _LOG_HANDLER.info(
        f"Tracer started with toplevel_trace_pid={toplevel_trace_pid} and report_basename={report_basename}")

    try:
        for _signal in (
                signal.SIGINT,
                signal.SIGTERM,
                signal.SIGHUP,
                signal.SIGABRT,
                signal.SIGQUIT,
        ):
            signal.signal(_signal, terminate_all_dispatchers)
    except ValueError: # Not main thread
        pass

    initialize_registry(report_basename)

    system_tracer_dispatcher = start_system_tracer_dispatcher(report_basename)
    _LOG_HANDLER.debug("System dispatcher started")

    main_tracer_dispatcher = start_main_tracer_dispatcher(toplevel_trace_pid, report_basename)
    _LOG_HANDLER.debug("Main dispatcher started")

    show_frontend(toplevel_trace_pid)

    # The main process had ended.
    terminate_all_dispatchers(signal.SIGTERM)  # Send signal.SIGINT to all dispatchers

    # Join the main dispatcher.
    main_tracer_dispatcher.join()
    _LOG_HANDLER.debug("Main dispatcher ended")

    # Join the system dispatcher.
    system_tracer_dispatcher.join()
    _LOG_HANDLER.debug("System dispatcher ended")

    # Make report
    make_all_report(_ALL_PIDS, report_basename)
    return 0


def initialize_registry(report_basename: str):
    """Initialize process registry."""
    with open(f"{report_basename}.reg.tsv", mode='a') as writer:
        writer.write('\t'.join((
            "TIME",
            "PID",
            "CMD",
            "EXE",
            "CWD"
        )) + '\n')


def start_system_tracer_dispatcher(report_basename: str) -> SystemTracerDispatcherThread:
    """
    Start system tracer dispatcher.
    """
    system_dispatcher_process = SystemTracerDispatcherThread(report_basename)
    system_dispatcher_process.start()
    _DISPATCHERS[0] = system_dispatcher_process
    return system_dispatcher_process


def start_main_tracer_dispatcher(toplevel_trace_pid: int, report_basename: str) -> ProcessTracerDispatcherThread:
    """
    Start the main dispatcher over traced process. If failed, suicide.
    """
    try:
        main_dispatcher = ProcessTracerDispatcherThread(toplevel_trace_pid, report_basename)
    except PSUTIL_NOTFOUND_ERRORS:
        print("Process not found -- Maybe it is terminated?")
        os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(0)
    _DISPATCHERS[toplevel_trace_pid] = main_dispatcher
    main_dispatcher.start()
    return main_dispatcher
