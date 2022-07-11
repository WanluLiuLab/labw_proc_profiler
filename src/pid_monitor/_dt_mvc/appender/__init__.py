import importlib
from typing import Type, Iterator, Tuple

from pid_monitor._dt_mvc.appender.typing import BaseTableAppender

POSSIBLE_APPENDER_PATHS = (
    "pid_monitor._dt_mvc.appender.tsv_appender",
    "pid_monitor._dt_mvc.appender.lzmatsv_appender",
    "pid_monitor._dt_mvc.appender.lz77tsv_appender",
    "pid_monitor._dt_mvc.appender.arrow_appender",
    "pid_monitor._dt_mvc.appender.dumb_appender",
    "pid_monitor._dt_mvc.appender.hdf5_appender",
    "pid_monitor._dt_mvc.appender.parquet_appender",
)

AVAILABLE_TABLE_APPENDERS = {
    "DumbTableAppender": 'DumbTableAppender',
    "TSVTableAppender": 'TSVTableAppender',
    "LZMATSVTableAppender": 'LZMATSVTableAppender',
    "LZ77TSVTableAppender": 'LZ77TSVTableAppender',
    #    "ArrowTableAppender": 'ArrowTableAppender', # bugs
    "HDF5TableAppender": 'HDF5TableAppender',
    "ParquetTableAppender": 'ParquetTableAppender',
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
