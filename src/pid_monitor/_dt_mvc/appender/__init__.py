import importlib
from typing import Type, Iterator, Tuple

from pid_monitor._dt_mvc.appender.typing import BaseTableAppender

POSSIBLE_APPENDER_PATHS = (
    "pid_monitor._dt_mvc.appender.tsv",
    "pid_monitor._dt_mvc.appender.csv",
    "pid_monitor._dt_mvc.appender.arrow",
    "pid_monitor._dt_mvc.appender.parquet",
    "pid_monitor._dt_mvc.appender.dumb"
)

AVAILABLE_TABLE_APPENDERS = {
    "TSVTableAppender": 'TSVTableAppender',
    "CSVTableAppender": 'CSVTableAppender',
    "ArrowTableAppender": 'ArrowTableAppender',
    "ParquetTableAppender": 'ParquetTableAppender',
    "DumbTableAppender": 'DumbTableAppender',
}


def load_table_appender_class(name: str) -> Type[BaseTableAppender]:
    """
    Return a known tracer.
    """
    for possible_path in POSSIBLE_APPENDER_PATHS:
        try:
            mod = importlib.import_module(possible_path)
            return getattr(mod, name)
        except (ModuleNotFoundError, AttributeError):
            continue
    raise ModuleNotFoundError


def list_table_appender() -> Iterator[Tuple[str, str]]:
    for possible_path in POSSIBLE_APPENDER_PATHS:
        try:
            mod = importlib.import_module(possible_path)

            for k, v in mod.__dict__.items():
                if k.__contains__("Appender") and not k.__contains__("Base"):
                    try:
                        yield k, v.__doc__.strip().splitlines()[0]
                    except AttributeError:
                        yield k, "No docs available"
        except ModuleNotFoundError:
            continue
