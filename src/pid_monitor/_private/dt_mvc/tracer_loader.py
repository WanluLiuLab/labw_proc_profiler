import importlib
from typing import Iterator, Tuple

POSSIBLE_TRACER_PATHS = (
    "pid_monitor._private.dt_mvc.std_tracer",
    "pid_monitor._private.dt_mvc.additional_tracer"
)


def get_tracer_class(name: str):
    """
    Return a known tracer.
    """
    for possible_path in POSSIBLE_TRACER_PATHS:
        try:
            mod = importlib.import_module(possible_path)
            return getattr(mod, name)
        except ModuleNotFoundError:
            continue
    raise ModuleNotFoundError


def list_tracer() -> Iterator[Tuple[str, str]]:
    """
    List all available tracer
    """
    for possible_path in POSSIBLE_TRACER_PATHS:
        try:
            mod = importlib.import_module(possible_path)
            for k, v in mod.__dict__.items():
                if k.__contains__("Tracer"):
                    try:
                        yield k, v.__doc__.strip().splitlines()[0]
                    except AttributeError:
                        yield k, "No docs available"
        except ModuleNotFoundError:
            continue
