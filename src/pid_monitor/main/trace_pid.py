import argparse
import logging
import os
import signal
import sys
from typing import List

from pid_monitor._dt_mvc import PSUTIL_NOTFOUND_ERRORS
from pid_monitor._dt_mvc.appender import load_table_appender_class, BaseTableAppender
from pid_monitor._dt_mvc.frontend import show_frontend
from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_dispatcher import DispatcherController
from pid_monitor._dt_mvc.std_dispatcher.process_tracer_dispatcher import ProcessTracerDispatcherThread
from pid_monitor._dt_mvc.std_dispatcher.system_tracer_dispatcher import SystemTracerDispatcherThread

_LOG_HANDLER = logging.getLogger()


def _start_system_tracer_dispatcher(
        pmc: PMConfig,
        dispatcher_controller: DispatcherController
) -> SystemTracerDispatcherThread:
    """
    Start system tracer dispatcher.
    """
    system_dispatcher_process = SystemTracerDispatcherThread(
        pmc=pmc,
        dispatcher_controller=dispatcher_controller
    )
    system_dispatcher_process.start()
    _LOG_HANDLER.debug("System dispatcher started")
    return system_dispatcher_process


def _create_registry_appender(pmc: PMConfig):
    return load_table_appender_class(
        pmc.table_appender_type
    )(
        filename=f"{pmc.output_basename}.reg",
        header=[
            "TIME",
            "PID",
            "CMD",
            "EXE",
            "CWD"
        ]
    )


def _start_main_tracer_dispatcher(
        trace_pid: int,
        pmc: PMConfig,
        dispatcher_controller: DispatcherController,
        registry_appender: BaseTableAppender
) -> ProcessTracerDispatcherThread:
    """
    Start the main dispatcher over traced process. If failed, suicide.
    """
    try:
        main_dispatcher = ProcessTracerDispatcherThread(
            trace_pid=trace_pid,
            pmc=pmc,
            dispatcher_controller=dispatcher_controller,
            registry_appender=registry_appender
        )
    except PSUTIL_NOTFOUND_ERRORS:
        _LOG_HANDLER.error(f"Process pid={trace_pid} not found -- Maybe it is terminated?")
        os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(0)
    main_dispatcher.start()
    _LOG_HANDLER.debug("Main dispatcher started")
    return main_dispatcher


def _parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser = PMConfig.append_pmc_args_to_argparser(parser)
    return parser.parse_args(args)


def trace_pid(
        pmc: PMConfig
) -> int:
    """
    The main entrance point

    You may use this function in your own projects.

    :param toplevel_trace_pid: The process ID to trace.
    :param output_basename: Basename of the report.
    :return: 0 for success.
    """
    _LOG_HANDLER.info(
        f"Tracer started with toplevel_trace_pid={pmc.toplevel_trace_pid} and output_basename={pmc.output_basename}"
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

    system_tracer_dispatcher = _start_system_tracer_dispatcher(
        pmc=pmc,
        dispatcher_controller=dispatcher_controller
    )
    _registry_appender = _create_registry_appender(pmc)
    main_tracer_dispatcher = _start_main_tracer_dispatcher(
        trace_pid=pmc.toplevel_trace_pid,
        pmc=pmc,
        dispatcher_controller=dispatcher_controller,
        registry_appender=_registry_appender
    )
    show_frontend(
        pmc=pmc,
        dispatcher_controller=dispatcher_controller
    )
    _registry_appender.close()
    dispatcher_controller.terminate_all_dispatchers(signal.SIGTERM)  # Send signal.SIGINT to all dispatchers

    main_tracer_dispatcher.join()
    _LOG_HANDLER.debug("Main dispatcher ended")

    system_tracer_dispatcher.join()
    _LOG_HANDLER.debug("System dispatcher ended")
    return 0


def main(args: List[str]):
    pmc = PMConfig.from_args(
        args=args
    )
    return trace_pid(
        pmc=pmc
    )
