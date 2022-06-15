def to_human_readable(
        num: int,
        base: int = 1024,
        suffix: str = "B"
) -> str:
    """
    Make an integer to 1000- or 1024-based human-readable form.
    """
    if base == 1024:
        dc_list = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']
    elif base == 1000:
        dc_list = ['', 'K', 'M', 'G', 'T', 'P', 'E']
    else:
        raise ValueError("base should be 1000 or 1024")
    step = 0
    dc = dc_list[step]
    while num > base and step < len(dc_list) - 1:
        step = step + 1
        num /= base
        dc = dc_list[step]
    num = round(num, 2)
    return str(num) + dc + suffix


def percent_to_str(num: float, total: float) -> str:
    if total != 0:
        return str(round(num/total * 100, 2)) + "%"
    else:
        return "NA"


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
