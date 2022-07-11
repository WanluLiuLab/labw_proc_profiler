import argparse
import os
from typing import List

from pid_monitor._dt_mvc.appender import AVAILABLE_TABLE_APPENDERS

DEFAULT_BACKEND_REFRESH_INTERVAL = 0.01
DEFAULT_FRONTEND_REFRESH_INTERVAL = 1
DEFAULT_PROCESS_LEVEL_TRACERS = [
    "ProcessIOTracerThread",
    "ProcessFDTracerThread",
    "ProcessMEMTracerThread",
    "ProcessChildTracerThread",
    "ProcessCPUTracerThread",
    "ProcessSTATTracerThread",
    "ProcessNFDTracerThread"
]
DEFAULT_SYSTEM_LEVEL_TRACERS = [
    "SystemMEMTracerThread",
    "SystemCPUTracerThread",
    "SystemSWAPTracerThread",
    #    "SystemConcurrentTracerThread"
]
DEFAULT_TABLE_APPENDER = "LZ77TSVTableAppender"
DEFAULT_TABLE_APPENDER_BUFFER_SIZE = 16
POSSIBLE_TRACER_PATHS = (
    "pid_monitor._dt_mvc.std_tracer.process_child_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.process_cpu_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.process_fd_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.process_io_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.process_mem_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.process_stat_tracer_thread",
    # "pid_monitor._dt_mvc.std_tracer.process_syscall_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.system_cpu_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.system_mem_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.system_swap_tracer_thread",
    # "pid_monitor._dt_mvc.std_tracer.system_concurrent_tracer_thread",
    "pid_monitor._dt_mvc.std_tracer.process_nfd_tracer_thread"
)

class PMConfig:
    output_basename: str
    backend_refresh_interval: float
    system_level_tracers_to_load: List[str]
    process_level_tracer_to_load: List[str]
    frontend_refresh_interval: float
    table_appender_type: str
    toplevel_trace_pid: int

    def __init__(
            self,
            toplevel_trace_pid: int,
            output_basename: str = None,
            backend_refresh_interval: float = DEFAULT_BACKEND_REFRESH_INTERVAL,
            system_level_tracers_to_load=None,
            process_level_tracer_to_load=None,
            frontend_refresh_interval: float = DEFAULT_FRONTEND_REFRESH_INTERVAL,
            table_appender_type: str = DEFAULT_TABLE_APPENDER,
            table_appender_buffer_size: int = DEFAULT_TABLE_APPENDER_BUFFER_SIZE
    ):
        if output_basename is None:
            os.makedirs(f"pid_monitor_{toplevel_trace_pid}", exist_ok=True)
            output_basename = os.path.join(f"pid_monitor_{toplevel_trace_pid}", "trace")
        if process_level_tracer_to_load is None:
            process_level_tracer_to_load = DEFAULT_PROCESS_LEVEL_TRACERS
        if system_level_tracers_to_load is None:
            system_level_tracers_to_load = DEFAULT_SYSTEM_LEVEL_TRACERS
        self.toplevel_trace_pid = toplevel_trace_pid
        self.output_basename = output_basename
        self.backend_refresh_interval = backend_refresh_interval
        self.system_level_tracers_to_load = system_level_tracers_to_load
        self.process_level_tracer_to_load = process_level_tracer_to_load
        self.frontend_refresh_interval = frontend_refresh_interval
        self.table_appender_type = table_appender_type
        self.table_appender_buffer_size = table_appender_buffer_size

    @classmethod
    def from_args(
            cls,
            args: List[str],
            disabled_args=None
    ):
        if disabled_args is None:
            disabled_args = []
        parser = PMConfig.append_pmc_args_to_argparser(argparse.ArgumentParser())
        parsed_args, _ = parser.parse_known_args(args)
        for disabled_arg in disabled_args:
            if parsed_args.__dict__[disabled_arg] is not None:
                raise ValueError(f"Arg {disabled_arg} is disabled!")
        newinstance = cls(
            toplevel_trace_pid=parsed_args.toplevel_trace_pid,
            output_basename=parsed_args.output_basename,
            backend_refresh_interval=parsed_args.backend_refresh_interval,
            frontend_refresh_interval=parsed_args.frontend_refresh_interval,
            system_level_tracers_to_load=parsed_args.system_level_tracers_to_load,
            process_level_tracer_to_load=parsed_args.process_level_tracer_to_load,
            table_appender_type=parsed_args.table_appender_type,
            table_appender_buffer_size=parsed_args.table_appender_buffer_size
        )
        return newinstance

    @staticmethod
    def append_pmc_args_to_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
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
            default=DEFAULT_PROCESS_LEVEL_TRACERS
        )
        parser.add_argument(
            "--system_level_tracers",
            help="Manually specify system_level_tracers",
            type=str,
            required=False,
            nargs='*',
            default=DEFAULT_SYSTEM_LEVEL_TRACERS
        )
        parser.add_argument(
            "--backend_refresh_interval",
            help="Manually specify interval",
            type=float,
            required=False,
            default=DEFAULT_BACKEND_REFRESH_INTERVAL
        )
        parser.add_argument(
            "--frontend_refresh_interval",
            help="Manually specify frontend_refresh_interval",
            type=float,
            required=False,
            default=DEFAULT_FRONTEND_REFRESH_INTERVAL
        )
        parser.add_argument(
            "--table_appender_type",
            help="Manually specify table_appender_type",
            type=str,
            choices=list(AVAILABLE_TABLE_APPENDERS.keys()),
            required=False,
            default=DEFAULT_TABLE_APPENDER
        )
        parser.add_argument(
            "--table_appender_buffer_size",
            help="Manually specify table_appender_buffer_size",
            type=int,
            required=False,
            default=DEFAULT_TABLE_APPENDER_BUFFER_SIZE
        )

        return parser
