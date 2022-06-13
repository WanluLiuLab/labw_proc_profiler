from typing import List

from pid_monitor._private.dt_mvc.tracer_loader import list_tracer


def main(_: List[str]):
    for tracer in list_tracer():
        print(": ".join(tracer))
    return 0
