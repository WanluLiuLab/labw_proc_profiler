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
