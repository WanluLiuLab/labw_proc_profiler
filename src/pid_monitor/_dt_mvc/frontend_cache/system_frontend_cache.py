from pid_monitor._dt_mvc.frontend_cache import percent_to_str, to_human_readable


class SystemFrontendCache:
    cpu_percent: float
    vm_avail: int
    vm_total: int
    vm_buffered: int
    vm_shared: int
    swap_total: int
    swap_used: int

    def __init__(self):
        self.cpu_percent = -1
        self.vm_avail = -1
        self.vm_shared = -1
        self.vm_total = -1
        self.vm_buffered = -1
        self.swap_total = -1
        self.swap_used = -1

    def __str__(self):
        swap_avail = self.swap_total - self.swap_used
        return "".join((
            "CPU%: ", percent_to_str(self.cpu_percent, 100), "; ",
            "VIRTUALMEM: ",
            "AVAIL: ", to_human_readable(self.vm_avail), "/", to_human_readable(self.vm_total),
            "=(", percent_to_str(self.vm_avail, self.vm_total), "), ",
            "BUFFERED: ", to_human_readable(self.vm_buffered), ", ",
            "SHARED: ", to_human_readable(self.vm_shared), "; ",
            "SWAP: ",
            "AVAIL: ", to_human_readable(swap_avail), "/", to_human_readable(self.swap_total),
            "=(", percent_to_str(swap_avail, self.swap_total), ") "
        ))
