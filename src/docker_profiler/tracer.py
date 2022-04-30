from __future__ import annotations

import threading
from abc import abstractmethod
from time import sleep
from typing import Tuple, List, Any, TextIO

import docker
from docker.errors import APIError, NotFound
from docker.models.containers import Container

from pid_monitor import get_timestamp

client = docker.from_env()


class DockerBaseTracerThread(threading.Thread):
    """
    The base class of all tracers.
    """
    traced_container: Container
    trace_container_name: str
    basename: str
    should_exit: bool  # Not used

    def __init__(self, trace_container_name: str, basename: str):
        super().__init__()
        try:
            self.traced_container = client.containers.get(trace_container_name)
        except (docker.errors.NotFound, APIError) as e:
            raise e
        self.trace_container_name = trace_container_name
        self.basename = basename
        self.should_exit = False


class DockerBaseWriterTracerThread(DockerBaseTracerThread):
    out_filename: str

    def __init__(self, trace_container_name: str, basename: str, tracee: str):
        super().__init__(trace_container_name=trace_container_name, basename=basename)
        self.out_filename = f"{self.basename}/{self.trace_container_name}.{tracee}.tsv"

    def parse_pid(self, stat: dict) -> int:
        total_pids = stat.get('pids_stats', {}).get('current', 0)
        return total_pids

    @abstractmethod
    def print_header(self, writer: TextIO):
        pass

    @abstractmethod
    def print_body(self, writer: TextIO):
        pass

    def run(self):
        with open(self.out_filename, "w") as writer:
            self.print_header(writer)
            while True:
                try:
                    self.print_body(writer)
                except (APIError, NotFound) as e:
                    raise e
                sleep(0.1)
                try:
                    if self.parse_pid(self.traced_container.stats(stream=False)) == 0:
                        return
                except (APIError, NotFound) as e:
                    raise e


class DockerStatsTracerThread(DockerBaseWriterTracerThread):
    """
    The base class of all tracers.
    """

    def __init__(self, trace_container_name: str, basename: str):
        super().__init__(trace_container_name, basename, "stat")

    def parse_cpu(self, stat: dict) -> Tuple[float, float]:
        container_cpu = stat.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0)
        pre_container_cpu = stat.get('precpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0)
        system_cpu = stat.get('cpu_stats', {}).get('system_cpu_usage', 0)
        pre_system_cpu = stat.get('precpu_stats', {}).get('system_cpu_usage', 0)
        num_cpu = stat.get('cpu_stats', {}).get('online_cpus', 0)
        container_cpu_diff = container_cpu - pre_container_cpu
        system_cpu_diff = system_cpu - pre_system_cpu
        if system_cpu_diff == 0:
            return 0, container_cpu
        else:
            return container_cpu_diff / system_cpu_diff * num_cpu, container_cpu

    def parse_memory(self, stat: dict) -> Tuple[float, float]:
        avail_memory = stat.get('memory_stats', {}).get('limit', 0)
        used_memory = stat.get('memory_stats', {}).get('usage', 0)
        return used_memory, avail_memory

    def print_header(self, writer: TextIO):
        writer.write(
            "\t".join((
                "ASCTIME",
                "CPU",
                "CPU_TIME",  # Measured in clock ticks
                "MEM_USED",
                "MEM_TOTAL",
                "NPROCS",
                "STATUS"
            )) + "\n"
        )

    def print_body(self, writer: TextIO):
        stat = self.traced_container.stats(stream=False)
        meminfo = self.parse_memory(stat)
        cpuinfo = self.parse_cpu(stat)
        pids = self.parse_pid(stat)
        writer.write(
            "\t".join((
                get_timestamp(),
                str(round(cpuinfo[0] * 100, 2)),
                str(cpuinfo[1]),
                str(meminfo[0]),
                str(meminfo[1]),
                str(pids),
                self.traced_container.status
            )) + "\n"
        )
        writer.flush()


class DockerTopTracerThread(DockerBaseWriterTracerThread):
    """
    The base class of all tracers.
    """

    def __init__(self, trace_container_name: str, basename: str):
        super().__init__(trace_container_name, basename, "top")

    def print_header(self, writer: TextIO):
        titles = self.traced_container.top().get("Titles", [])
        writer.write(
            "ASCTIME" + "\t" + "\t".join(titles) + "\n"
        )

    def print_body(self, writer: TextIO):
        timestamp = get_timestamp()
        top = self.traced_container.top()
        for process in top.get('Processes', []):
            writer.write(
                timestamp + "\t" + "\t".join(process) + "\n"
            )
        writer.flush()


class DockerDispatcherThread(DockerBaseTracerThread):
    """
    The base class of all tracers.
    """
    tracers: List[DockerBaseTracerThread]

    def __init__(self, trace_container_name: str, basename: str):
        super().__init__(trace_container_name, basename)
        self.tracers = []

    def run(self):
        for cls in (
                DockerStatsTracerThread,
                DockerTopTracerThread
        ):
            try:
                self.tracers.append(cls(self.trace_container_name, self.basename))
                self.tracers[-1].start()
            except (NotFound, APIError) as e:
                raise e
        for tracer in self.tracers:
            tracer.join()
        with open(f"{self.basename}/{self.trace_container_name}.stdout.log", "wb") as stdout_writer:
            stdout_writer.write(self.traced_container.logs(stdout=True, stderr=False, timestamps=True))
        with open(f"{self.basename}/{self.trace_container_name}.stderr.log", "wb") as stderr_writer:
            stderr_writer.write(self.traced_container.logs(stdout=False, stderr=True, timestamps=True))
        with open(f"{self.basename}/{self.trace_container_name}.info.tsv", "w") as info_writer:
            def k_v_write(k: str, v: Any):
                rv = repr(v)
                if len(rv) >= 2 and rv[0] == '\'' and rv[-1] == '\'':
                    rv = rv[1:-1]
                info_writer.write("\t".join((k, rv)) + "\n")

            k_v_write("KEY", "VALUE")
            k_v_write("NAME", self.traced_container.name)
            k_v_write("ID", self.traced_container.id)
            k_v_write("IMAGE_ID", self.traced_container.image.id)
            k_v_write("IMAGE_TAGS", self.traced_container.image.tags)
            k_v_write("LABELS", self.traced_container.labels)
