from typing import List

from pid_monitor._dt_mvc.frontend_cache import percent_to_str, to_human_readable


class ProcessFrontendCache:
    pid: int
    ppid: int
    name: str
    cpu_percent: float
    stat: str
    cpu_time: float
    resident_mem: int
    num_threads: int
    num_child_processes: int

    def __init__(
            self,
            name: str,
            pid: int,
            ppid: int
    ):
        """
        Setup cached values
        """
        self.pid = pid
        self.cpu_time = -1
        self.cpu_percent = -1
        self.stat = "NA"
        self.resident_mem = -1
        self.num_threads = -1
        self.num_child_processes = -1
        self.name = name
        self.ppid = ppid

    def to_prettytable_row(self) -> List[str]:
        return list(map(
            lambda x: repr(x).replace('\'', '').replace('\"', ''),
            (
                self.pid,
                self.ppid,
                self.name,
                self.stat,
                percent_to_str(self.cpu_percent, 100),
                f"{self.cpu_time:.2f}",
                to_human_readable(self.resident_mem),
                self.num_threads,
                self.num_child_processes
            )
        ))
