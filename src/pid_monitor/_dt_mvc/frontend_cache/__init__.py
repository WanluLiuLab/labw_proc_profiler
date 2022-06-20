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
    return f"{num:.2f}{dc}{suffix}"


def percent_to_str(num: float, total: float) -> str:
    if total != 0:
        return f"{num / total * 100:.2f}%"
    else:
        return "NA"
