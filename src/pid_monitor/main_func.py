"""
This module contains main function of pid_monitor and can be used in other projects.
"""

import logging
import os
import signal
import sys
from typing import List

from pid_monitor import PSUTIL_NOTFOUND_ERRORS, DEFAULT_PROCESS_LEVEL_TRACERS, DEFAULT_SYSTEM_LEVEL_TRACERS, \
    DEFAULT_REFRESH_INTERVAL
from pid_monitor.dt_mvc.base_dispatcher_class import DispatcherController
from pid_monitor.dt_mvc.std_dispatcher import SystemTracerDispatcherThread, ProcessTracerDispatcherThread
from pid_monitor.frontend import show_frontend
from pid_monitor.report import make_all_report

_LOG_HANDLER = logging.getLogger()
"""The Logger Handler"""


def _initialize_registry(report_basename: str):
    """Initialize process registry."""
    with open(f"{report_basename}.reg.tsv", mode='a') as writer:
        writer.write('\t'.join((
            "TIME",
            "PID",
            "CMD",
            "EXE",
            "CWD"
        )) + '\n')


def _start_system_tracer_dispatcher(
        report_basename: str,
        system_level_tracers: List[str],
        interval: float,
        dispatcher_controller: DispatcherController
) -> SystemTracerDispatcherThread:
    """
    Start system tracer dispatcher.
    """
    system_dispatcher_process = SystemTracerDispatcherThread(
        basename=report_basename,
        tracers_to_load=system_level_tracers,
        interval=interval,
        dispatcher_controller=dispatcher_controller
    )
    system_dispatcher_process.start()
    _LOG_HANDLER.debug("System dispatcher started")
    return system_dispatcher_process


def _start_main_tracer_dispatcher(
        toplevel_trace_pid: int,
        report_basename: str,
        process_level_tracers: List[str],
        interval: float,
        dispatcher_controller: DispatcherController
) -> ProcessTracerDispatcherThread:
    """
    Start the main dispatcher over traced process. If failed, suicide.
    """
    try:
        main_dispatcher = ProcessTracerDispatcherThread(
            trace_pid=toplevel_trace_pid,
            basename=report_basename,
            tracers_to_load=process_level_tracers,
            interval=interval,
            dispatcher_controller=dispatcher_controller
        )
    except PSUTIL_NOTFOUND_ERRORS:
        _LOG_HANDLER.error(f"Process pid={toplevel_trace_pid} not found -- Maybe it is terminated?")
        os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(0)
    main_dispatcher.start()
    _LOG_HANDLER.debug("Main dispatcher started")
    return main_dispatcher


def trace_pid(
        toplevel_trace_pid: int,
        report_basename: str,
        process_level_tracers: List[str] = DEFAULT_PROCESS_LEVEL_TRACERS,
        system_level_tracers: List[str] = DEFAULT_SYSTEM_LEVEL_TRACERS,
        interval: float = DEFAULT_REFRESH_INTERVAL,
        make_report: bool = True
) -> int:
    """
    The main entrance point

    You may use this function in your own projects.

    :param toplevel_trace_pid: The process ID to trace.
    :param report_basename: Basename of the report.
    :return: 0 for success.
    """
    _LOG_HANDLER.info(
        f"Tracer started with toplevel_trace_pid={toplevel_trace_pid} and report_basename={report_basename}"
    )
    dispatcher_controller = DispatcherController()

    try:
        for _signal in (
                signal.SIGINT,
                signal.SIGTERM,
                signal.SIGHUP,
                signal.SIGABRT,
                signal.SIGQUIT,
        ):
            signal.signal(_signal, dispatcher_controller.terminate_all_dispatchers)
    except ValueError:  # Not main thread
        pass

    _initialize_registry(report_basename)
    system_tracer_dispatcher = _start_system_tracer_dispatcher(
        report_basename=report_basename,
        system_level_tracers=system_level_tracers,
        interval=interval,
        dispatcher_controller=dispatcher_controller
    )
    main_tracer_dispatcher = _start_main_tracer_dispatcher(
        toplevel_trace_pid=toplevel_trace_pid,
        report_basename=report_basename,
        process_level_tracers=process_level_tracers,
        interval=interval,
        dispatcher_controller=dispatcher_controller
    )
    show_frontend(
        interval=interval,
        dispatcher_controller=dispatcher_controller
    )
    dispatcher_controller.terminate_all_dispatchers(signal.SIGTERM)  # Send signal.SIGINT to all dispatchers

    main_tracer_dispatcher.join()
    _LOG_HANDLER.debug("Main dispatcher ended")

    system_tracer_dispatcher.join()
    _LOG_HANDLER.debug("System dispatcher ended")

    # Make report
    if make_report:
        make_all_report(dispatcher_controller.all_pids, report_basename)
    return 0
