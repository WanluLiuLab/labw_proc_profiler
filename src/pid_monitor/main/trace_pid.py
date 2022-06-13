import argparse
import logging
import os
import signal
import sys
from typing import List

from pid_monitor._private import PSUTIL_NOTFOUND_ERRORS, DEFAULT_PROCESS_LEVEL_TRACERS, DEFAULT_SYSTEM_LEVEL_TRACERS, \
    DEFAULT_REFRESH_INTERVAL
from pid_monitor._private.dt_mvc.base_dispatcher_class import DispatcherController
from pid_monitor._private.dt_mvc.std_dispatcher import SystemTracerDispatcherThread, ProcessTracerDispatcherThread
from pid_monitor._private.frontend import show_frontend
from pid_monitor._private.report import make_all_report

_LOG_HANDLER = logging.getLogger()


def _initialize_registry(output_basename: str):
    """Initialize process registry."""
    with open(f"{output_basename}.reg.tsv", mode='a') as writer:
        writer.write('\t'.join((
            "TIME",
            "PID",
            "CMD",
            "EXE",
            "CWD"
        )) + '\n')


def _start_system_tracer_dispatcher(
        output_basename: str,
        system_level_tracers: List[str],
        interval: float,
        dispatcher_controller: DispatcherController
) -> SystemTracerDispatcherThread:
    """
    Start system tracer dispatcher.
    """
    system_dispatcher_process = SystemTracerDispatcherThread(
        basename=output_basename,
        tracers_to_load=system_level_tracers,
        interval=interval,
        dispatcher_controller=dispatcher_controller
    )
    system_dispatcher_process.start()
    _LOG_HANDLER.debug("System dispatcher started")
    return system_dispatcher_process


def _start_main_tracer_dispatcher(
        toplevel_trace_pid: int,
        output_basename: str,
        process_level_tracers: List[str],
        interval: float,
        dispatcher_controller: DispatcherController
) -> ProcessTracerDispatcherThread:
    """
    Start the main dispatcher over traced process. If failed, suicide.
    """
    try:
        main_dispatcher = ProcessTracerDispatcherThread(trace_pid=toplevel_trace_pid, output_basename=output_basename,
                                                        tracers_to_load=process_level_tracers, interval=interval,
                                                        dispatcher_controller=dispatcher_controller)
    except PSUTIL_NOTFOUND_ERRORS:
        _LOG_HANDLER.error(f"Process pid={toplevel_trace_pid} not found -- Maybe it is terminated?")
        os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(0)
    main_dispatcher.start()
    _LOG_HANDLER.debug("Main dispatcher started")
    return main_dispatcher

def _parse_args(args:List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--pid",
        help="PID to trace",
        type=int,
        required=True
    )
    parser.add_argument(
        "-o", "--out",
        help="Basename of output files",
        type=str,
        required=False,
        default=None
    )
    parser.add_argument(
        "--process_level_tracers",
        help="Manually specify process_level_tracers",
        type=str,
        required=False,
        nargs='*',
        default=None
    )
    parser.add_argument(
        "--system_level_tracers",
        help="Manually specify system_level_tracers",
        type=str,
        required=False,
        nargs='*',
        default=None
    )
    parser.add_argument(
        "--interval",
        help="Manually specify interval",
        type=float,
        required=False,
        default=None
    )
    parser.add_argument(
        "--not_make_report",
        help="Trace without making report",
        required=False,
        action="store_true",
        default=False
    )
    return parser.parse_args(args)

def trace_pid(
        toplevel_trace_pid: int,
        output_basename: str,
        process_level_tracers: List[str] = DEFAULT_PROCESS_LEVEL_TRACERS,
        system_level_tracers: List[str] = DEFAULT_SYSTEM_LEVEL_TRACERS,
        interval: float = DEFAULT_REFRESH_INTERVAL,
        make_report: bool = True
) -> int:
    """
    The main entrance point

    You may use this function in your own projects.

    :param toplevel_trace_pid: The process ID to trace.
    :param output_basename: Basename of the report.
    :return: 0 for success.
    """
    _LOG_HANDLER.info(
        f"Tracer started with toplevel_trace_pid={toplevel_trace_pid} and output_basename={output_basename}"
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

    _initialize_registry(output_basename)
    system_tracer_dispatcher = _start_system_tracer_dispatcher(
        output_basename=output_basename,
        system_level_tracers=system_level_tracers,
        interval=interval,
        dispatcher_controller=dispatcher_controller
    )
    main_tracer_dispatcher = _start_main_tracer_dispatcher(
        toplevel_trace_pid=toplevel_trace_pid,
        output_basename=output_basename,
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
        print(list(dispatcher_controller.all_pids))
        make_all_report(dispatcher_controller.all_pids, output_basename)
    return 0

def main(args:List[str]):
    args=_parse_args(args)
    trace_pid_kwargs={
        "toplevel_trace_pid":args.pid
    }
    if args.out is None:
        os.makedirs(f"pid_monitor_{args.pid}", exist_ok=True)
        trace_pid_kwargs["output_basename"] = os.path.join(f"pid_monitor_{args.pid}", "trace")
    if args.process_level_tracers is not None:
        trace_pid_kwargs["process_level_tracers"] = args.process_level_tracers
    if args.system_level_tracers is not None:
        trace_pid_kwargs["system_level_tracers"] = args.system_level_tracers
    if args.interval is not None:
        trace_pid_kwargs["interval"] = args.interval
    trace_pid_kwargs["make_report"] = not args.not_make_report
    return trace_pid(**trace_pid_kwargs)
